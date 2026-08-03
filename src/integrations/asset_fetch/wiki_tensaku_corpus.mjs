#!/usr/bin/env node

/**
 * Public-source collector for the Miko-led unofficial-wiki review family.
 *
 * Network activity is confined to asset_fetch. The collector inventories the
 * current public channel surfaces, fetches public watch metadata and automatic
 * caption payloads, and can acquire one low-resolution combined A/V source for
 * an internal diagnostic build. It never uploads, authenticates, changes
 * visibility, or claims rights/publication approval.
 */

import { createHash } from "node:crypto";
import { createWriteStream, existsSync } from "node:fs";
import { mkdir, readFile, rename, rm, stat, writeFile } from "node:fs/promises";
import { dirname, join, resolve } from "node:path";
import { Readable } from "node:stream";
import { pipeline } from "node:stream/promises";

const SCHEMA_VERSION = "clippipegen.wiki_tensaku_corpus.v1";
const DEFAULT_ARTIFACT_ID = "clip-wiki-tensaku-longform-v1-001";
const CHANNEL_HANDLE = "SakuraMiko";
const CHANNEL_ID = "UC-hM6YJuNYVAmUWxeIr9FeA";
const CHANNEL_NAME = "Miko Ch. さくらみこ";
const CHANNEL_BASE = `https://www.youtube.com/@${CHANNEL_HANDLE}`;
const FAMILY_TITLE_PATTERN = /(非公式\s*wiki|みこスバ調査隊)/iu;
const PLAYLIST_TITLE_PATTERN = /(wiki|ウィキ|添削|みこスバ調査隊)/iu;
const SEARCH_QUERIES = [
  "Wiki添削",
  "非公式wiki さくらみこ",
  "みこスバ調査隊",
];
const DEFAULT_MAX_PAGES = 120;
const SLICE_TARGET_SECONDS = 300;
const VIDEO_ID_PATTERN = /^[A-Za-z0-9_-]{11}$/u;
const ARTIFACT_ID_PATTERN = /^clip-[a-z0-9][a-z0-9-]*$/u;
const ANDROID_CLIENT = {
  clientName: "ANDROID",
  clientVersion: "20.10.38",
  androidSdkVersion: 30,
  hl: "ja",
  gl: "JP",
};
const WEB_HEADERS = {
  "user-agent": "Mozilla/5.0",
  "accept-language": "ja,en;q=0.8",
};
const JSON_HEADERS = { ...WEB_HEADERS, "content-type": "application/json" };

const TOPICS = [
  {
    id: "profile_and_biography",
    label: "プロフィール・来歴",
    pattern: /(プロフィール|経歴|デビュー|出身|生まれ|年齢|誕生日)/u,
  },
  {
    id: "quoted_phrases_and_wording",
    label: "語録・言い回し",
    pattern: /(語録|名言|言い間違|滑舌|発言|言葉)/u,
  },
  {
    id: "relationships_and_collaborations",
    label: "関係性・共演",
    pattern: /(スバル|みこ|マリン|ねね|ホロメン|コラボ|共演)/u,
  },
  {
    id: "correction_and_verification",
    label: "訂正・事実確認",
    pattern: /(違う|間違|訂正|修正|本当|事実|嘘|正しく|更新)/u,
  },
  {
    id: "before_after_change",
    label: "前後・変化",
    pattern: /(昔|今|現在|当時|前は|後で|変わ|更新)/u,
  },
];
const CORRECTION_PATTERN = /(違う|間違|訂正|修正|本当|事実|嘘|正しく|更新)/u;

function parseArgs(argv) {
  const args = {
    outputDir: null,
    maxPages: DEFAULT_MAX_PAGES,
    downloadSelectedSource: false,
    selectedVideoId: null,
    artifactId: DEFAULT_ARTIFACT_ID,
    reuseInventory: false,
  };
  for (let index = 0; index < argv.length; index += 1) {
    const value = argv[index];
    if (value === "--output-dir") args.outputDir = argv[++index];
    else if (value === "--max-pages") args.maxPages = Number(argv[++index]);
    else if (value === "--download-first-source" || value === "--download-selected-source") {
      args.downloadSelectedSource = true;
    } else if (value === "--slice-video-id") args.selectedVideoId = argv[++index];
    else if (value === "--artifact-id") args.artifactId = argv[++index];
    else if (value === "--reuse-inventory") args.reuseInventory = true;
    else if (value === "--help" || value === "-h") args.help = true;
    else throw new Error(`unknown argument: ${value}`);
  }
  if (args.help) return args;
  if (!args.outputDir) throw new Error("--output-dir is required");
  if (!Number.isInteger(args.maxPages) || args.maxPages < 1) {
    throw new Error("--max-pages must be a positive integer");
  }
  if (args.selectedVideoId && !VIDEO_ID_PATTERN.test(args.selectedVideoId)) {
    throw new Error("--slice-video-id must be an 11-character YouTube video ID");
  }
  if (!ARTIFACT_ID_PATTERN.test(args.artifactId)) {
    throw new Error("--artifact-id must be a lowercase clip-* identity");
  }
  if (args.reuseInventory && !args.selectedVideoId) {
    throw new Error("--reuse-inventory requires --slice-video-id");
  }
  return args;
}

function usage() {
  return [
    "node src/integrations/asset_fetch/wiki_tensaku_corpus.mjs \\",
    "  --output-dir episodes/wiki_tensaku_family_20260804/corpus \\",
    "  [--max-pages 120] [--download-first-source]",
    "",
    "Existing-corpus successor slice:",
    "  --reuse-inventory --slice-video-id <id> --artifact-id <clip-*> \\",
    "  [--download-selected-source]",
  ].join("\n");
}

async function fetchText(url, init = {}) {
  const response = await fetch(url, { ...init, headers: { ...WEB_HEADERS, ...(init.headers || {}) } });
  if (!response.ok) throw new Error(`GET ${scrubUrl(url)} failed: ${response.status}`);
  return response.text();
}

function extractAssignedJson(html, marker) {
  const start = html.indexOf(marker);
  if (start < 0) throw new Error(`missing page marker: ${marker}`);
  const end = html.indexOf(";</script>", start);
  if (end < 0) throw new Error(`unterminated page marker: ${marker}`);
  return JSON.parse(html.slice(start + marker.length, end));
}

function pageConfig(html) {
  const apiKey = html.match(/"INNERTUBE_API_KEY":"([^"]+)"/)?.[1];
  const clientVersion = html.match(/"INNERTUBE_CLIENT_VERSION":"([^"]+)"/)?.[1];
  if (!apiKey || !clientVersion) throw new Error("YouTube public page config missing");
  return { apiKey, clientVersion };
}

function lockups(items, contentType) {
  const rows = [];
  function walk(value) {
    if (!value || typeof value !== "object") return;
    const model = value.lockupViewModel;
    if (model?.contentType === contentType) {
      const metadata = model.metadata?.lockupMetadataViewModel;
      rows.push({
        id: model.contentId,
        title: metadata?.title?.content || "",
        surface_metadata: (metadata?.metadata?.contentMetadataViewModel?.metadataRows || [])
          .flatMap((row) => row.metadataParts || [])
          .map((part) => part.text?.content)
          .filter(Boolean),
      });
    }
    for (const child of Object.values(value)) walk(child);
  }
  walk(items || []);
  return rows;
}

function nextContinuation(items) {
  let token = null;
  function walk(value) {
    if (!value || typeof value !== "object" || token) return;
    token = value.continuationItemRenderer?.continuationEndpoint
      ?.continuationCommand?.token || null;
    if (token) return;
    for (const child of Object.values(value)) walk(child);
  }
  walk(items || []);
  return token;
}

function selectedGrid(initialData) {
  const tabs = initialData?.contents?.twoColumnBrowseResultsRenderer?.tabs || [];
  const selected = tabs.find((tab) => tab.tabRenderer?.selected)?.tabRenderer;
  let grid = selected?.content?.richGridRenderer || null;
  if (!grid) {
    function walk(value) {
      if (!value || typeof value !== "object" || grid) return;
      if (value.richGridRenderer) {
        grid = value.richGridRenderer;
        return;
      }
      for (const child of Object.values(value)) walk(child);
    }
    walk(selected?.content);
  }
  if (grid) return { title: selected.title || null, items: grid.contents || [] };
  if (!selected?.content) throw new Error("selected public channel tab has no item surface");
  return { title: selected.title || null, items: [selected.content] };
}

function appendedItems(payload) {
  const found = [];
  function walk(value) {
    if (!value || typeof value !== "object") return;
    if (value.appendContinuationItemsAction?.continuationItems) {
      found.push(...value.appendContinuationItemsAction.continuationItems);
    }
    for (const child of Object.values(value)) walk(child);
  }
  walk(payload);
  return found;
}

async function crawlChannelTab({ url, contentType, maxPages }) {
  const html = await fetchText(url);
  const config = pageConfig(html);
  const initial = extractAssignedJson(html, "var ytInitialData = ");
  const grid = selectedGrid(initial);
  let items = grid.items;
  let rows = lockups(items, contentType);
  let token = nextContinuation(items);
  let pages = 1;
  let continuationRequests = 0;
  const continuationTokenHashes = [];
  while (token && pages < maxPages) {
    continuationTokenHashes.push(sha256Text(token));
    const response = await fetch(`https://www.youtube.com/youtubei/v1/browse?key=${config.apiKey}`, {
      method: "POST",
      headers: JSON_HEADERS,
      body: JSON.stringify({
        context: { client: { clientName: "WEB", clientVersion: config.clientVersion, hl: "ja", gl: "JP" } },
        continuation: token,
      }),
    });
    if (!response.ok) throw new Error(`channel continuation ${pages + 1} failed: ${response.status}`);
    items = appendedItems(await response.json());
    rows.push(...lockups(items, contentType));
    token = nextContinuation(items);
    pages += 1;
    continuationRequests += 1;
  }
  const unique = [...new Map(rows.map((row) => [row.id, row])).values()];
  return {
    url,
    tab_title: grid.title,
    pages,
    continuation_requests: continuationRequests,
    continuation_token_sha256s: continuationTokenHashes,
    pagination_exhausted: !token,
    truncated_by_max_pages: Boolean(token),
    raw_count: rows.length,
    unique_count: unique.length,
    duplicate_count: rows.length - unique.length,
    rows: unique,
  };
}

function parseSearchResults(initial) {
  const rows = [];
  function walk(value) {
    if (!value || typeof value !== "object") return;
    if (value.videoRenderer) {
      const row = value.videoRenderer;
      rows.push({
        id: row.videoId,
        title: (row.title?.runs || []).map((part) => part.text || "").join(""),
        channel: (row.ownerText?.runs || row.shortBylineText?.runs || [])
          .map((part) => part.text || "").join(""),
        channel_id: row.ownerText?.runs?.[0]?.navigationEndpoint?.browseEndpoint?.browseId || null,
        published: row.publishedTimeText?.simpleText || null,
        length: row.lengthText?.simpleText || null,
      });
    }
    for (const child of Object.values(value)) walk(child);
  }
  walk(initial);
  return [...new Map(rows.map((row) => [row.id, row])).values()];
}

async function collectSearchSurface(query) {
  const url = `https://www.youtube.com/results?search_query=${encodeURIComponent(query)}`;
  const html = await fetchText(url);
  const initial = extractAssignedJson(html, "var ytInitialData = ");
  const rows = parseSearchResults(initial);
  return {
    query,
    url,
    page_count: 1,
    pagination_policy: "bounded_auxiliary_first_page_not_used_for_completeness",
    result_count: rows.length,
    rows,
  };
}

function parsePlayerResponse(html) {
  return extractAssignedJson(html, "var ytInitialPlayerResponse = ");
}

async function collectWatch(videoId, { fetchCaption = true } = {}) {
  const url = `https://www.youtube.com/watch?v=${videoId}&hl=ja`;
  const html = await fetchText(url);
  const player = parsePlayerResponse(html);
  const video = player.videoDetails || {};
  const micro = player.microformat?.playerMicroformatRenderer || {};
  const android = await androidPlayer(videoId, html);
  const tracks = android.captions?.playerCaptionsTracklistRenderer?.captionTracks
    || player.captions?.playerCaptionsTracklistRenderer?.captionTracks
    || [];
  const japanese = tracks.find((track) => track.languageCode === "ja") || null;
  let captionPayload = null;
  let captionStatus = "absent";
  if (fetchCaption && japanese?.baseUrl) {
    const captionUrl = new URL(japanese.baseUrl);
    captionUrl.searchParams.set("fmt", "json3");
    const response = await fetch(captionUrl, { headers: WEB_HEADERS });
    if (response.ok) {
      const payloadText = await response.text();
      if (payloadText.trim()) {
        try {
          captionPayload = JSON.parse(payloadText);
          captionStatus = "fetched";
        } catch {
          captionStatus = "invalid_json";
        }
      } else {
        captionStatus = "empty_payload";
      }
    } else {
      captionStatus = `http_${response.status}`;
    }
  }
  if (!fetchCaption && japanese) captionStatus = "existing_payload_reused_not_refetched";
  return {
    receipt: {
      schema_version: SCHEMA_VERSION,
      video_id: videoId,
      url: `https://www.youtube.com/watch?v=${videoId}`,
      title: video.title || null,
      channel: video.author || null,
      channel_id: video.channelId || null,
      publish_timestamp: micro.publishDate || null,
      upload_timestamp: micro.uploadDate || null,
      duration_seconds: Number(video.lengthSeconds || 0),
      availability: player.playabilityStatus?.status || "UNKNOWN",
      availability_reason: player.playabilityStatus?.reason || null,
      archived_livestream: Boolean(video.isLiveContent),
      caption: {
        status: captionStatus,
        language_code: japanese?.languageCode || null,
        name: japanese?.name?.simpleText || japanese?.name?.runs?.map((part) => part.text).join("") || null,
        kind: japanese?.kind || null,
        provider_authorship_claim: false,
      },
      description_sha256: sha256Text(video.shortDescription || ""),
    },
    captionPayload,
    html,
  };
}

function captionEvents(payload) {
  const events = [];
  for (let index = 0; index < (payload?.events || []).length; index += 1) {
    const row = payload.events[index];
    const text = (row.segs || []).map((segment) => segment.utf8 || "").join("")
      .replace(/\s+/gu, " ").trim();
    const start = Number(row.tStartMs || 0) / 1000;
    const duration = Number(row.dDurationMs || 0) / 1000;
    if (!text || duration <= 0) continue;
    events.push({
      event_id: `event_${String(index).padStart(6, "0")}`,
      source_start_seconds: round6(start),
      source_end_seconds: round6(start + duration),
      text,
      text_sha256: sha256Text(text),
      provenance_type: "source_caption",
      authority: "youtube_automatic_caption_unreviewed",
    });
  }
  return events;
}

function scoreTopics(text) {
  const scores = {};
  for (const topic of TOPICS) scores[topic.id] = topic.pattern.test(text) ? 1 : 0;
  return scores;
}

function buildTopicIndex(inventory, captionById) {
  const sources = [];
  for (const item of inventory) {
    const events = captionEvents(captionById.get(item.video_id));
    const windows = new Map();
    const corrections = [];
    for (let index = 0; index < events.length; index += 1) {
      const event = events[index];
      const windowStart = Math.floor(event.source_start_seconds / 300) * 300;
      const key = String(windowStart);
      if (!windows.has(key)) {
        windows.set(key, {
          source_start_seconds: windowStart,
          source_end_seconds: Math.min(item.duration_seconds, windowStart + 300),
          event_ids: [],
          topic_scores: Object.fromEntries(TOPICS.map((topic) => [topic.id, 0])),
        });
      }
      const window = windows.get(key);
      window.event_ids.push(event.event_id);
      for (const [topicId, score] of Object.entries(scoreTopics(event.text))) {
        window.topic_scores[topicId] += score;
      }
      if (CORRECTION_PATTERN.test(event.text)) {
        corrections.push({
          anchor_event_id: event.event_id,
          source_start_seconds: event.source_start_seconds,
          source_end_seconds: event.source_end_seconds,
          text_sha256: event.text_sha256,
          context_before_event_ids: events.slice(Math.max(0, index - 2), index).map((row) => row.event_id),
          context_after_event_ids: events.slice(index + 1, index + 3).map((row) => row.event_id),
          relationship_status: "context_window_only_no_causality_inferred",
        });
      }
    }
    const ranked = [...windows.values()]
      .map((window) => ({
        ...window,
        dominant_topics: Object.entries(window.topic_scores)
          .filter(([, score]) => score > 0)
          .sort((left, right) => right[1] - left[1])
          .slice(0, 3)
          .map(([id, score]) => ({ id, score })),
      }))
      .sort((left, right) => left.source_start_seconds - right.source_start_seconds);
    sources.push({
      video_id: item.video_id,
      caption_event_count: events.length,
      topic_windows: ranked,
      correction_anchors: corrections,
      semantic_status: "machine_keyword_index_requires_editorial_review",
    });
  }
  return {
    schema_version: SCHEMA_VERSION,
    source_caption_track: {
      provenance_type: "source_caption",
      authority: "youtube_automatic_caption_unreviewed",
    },
    creator_commentary_track: {
      provenance_type: "creator_authored_commentary",
      authority: "ClipPipeGen editorial layer",
      merged_with_source_caption: false,
    },
    sources,
  };
}

function expectedUniformCuts(sourceDuration, targetDuration) {
  const desired = Math.min(sourceDuration, targetDuration);
  let count = Math.max(8, Math.min(20, roundHalfEven(desired / 24)));
  if (desired / count < 5) count = Math.max(1, Math.floor(desired / 5));
  const slot = sourceDuration / count;
  const segment = desired / count;
  const cuts = [];
  let previousEnd = 0;
  for (let index = 0; index < count; index += 1) {
    const center = (index + 0.5) * slot;
    const start = Math.max(previousEnd, center - segment / 2);
    const end = Math.min(sourceDuration, start + segment);
    cuts.push({ start: round6(start), end: round6(end) });
    previousEnd = end;
  }
  return cuts;
}

const SUCCESSOR_CHAPTER_PHASES = [
  "導入と調査対象",
  "プロフィールの入口",
  "語録と表現",
  "関係性の照合",
  "記述のズレ",
  "訂正点の掘り下げ",
  "過去と現在",
  "共演者の視点",
  "事実確認",
  "更新される人物像",
  "終盤の再照合",
  "総括と残る論点",
];

function buildEditorialContext(
  source,
  captionPayload,
  {
    artifactId = DEFAULT_ARTIFACT_ID,
    sourceDurationBasis = "provider_combined_format_approx_duration",
  } = {},
) {
  const events = captionEvents(captionPayload);
  const uniformCuts = expectedUniformCuts(source.duration_seconds, SLICE_TARGET_SECONDS);
  const slotSeconds = source.duration_seconds / uniformCuts.length;
  const segmentSeconds = SLICE_TARGET_SECONDS / uniformCuts.length;
  const successorStyle = artifactId !== DEFAULT_ARTIFACT_ID;
  const cuts = uniformCuts.map((fallback, index) => {
    const slotStart = index * slotSeconds;
    const slotEnd = (index + 1) * slotSeconds;
    const candidates = events
      .filter((event) => event.source_start_seconds >= slotStart && event.source_start_seconds < slotEnd)
      .map((event) => Math.min(
        Math.max(slotStart, event.source_start_seconds - 5),
        slotEnd - segmentSeconds,
      ));
    if (!candidates.length) return fallback;
    let best = fallback;
    let bestScore = -1;
    for (const start of candidates) {
      const end = start + segmentSeconds;
      const evidence = events.filter((event) =>
        Math.min(event.source_end_seconds, end) - Math.max(event.source_start_seconds, start) > 0.02
      );
      const topicScore = evidence.reduce(
        (total, event) => total + Object.values(scoreTopics(event.text)).reduce((sum, value) => sum + value, 0),
        0,
      );
      const score = evidence.length * 10 + topicScore;
      if (score > bestScore || (score === bestScore && start < best.start)) {
        best = { start: round6(start), end: round6(end) };
        bestScore = score;
      }
    }
    return best;
  });
  const chapters = cuts.map((range, index) => {
    const evidence = events.filter((event) =>
      Math.min(event.source_end_seconds, range.end) - Math.max(event.source_start_seconds, range.start) > 0.02
    );
    const topicScores = Object.fromEntries(TOPICS.map((topic) => [topic.id, 0]));
    for (const event of evidence) {
      for (const [topicId, score] of Object.entries(scoreTopics(event.text))) topicScores[topicId] += score;
    }
    const topics = Object.entries(topicScores).filter(([, score]) => score > 0)
      .sort((left, right) => right[1] - left[1]);
    const topicLabels = topics.slice(0, 3).map(([id]) => TOPICS.find((topic) => topic.id === id)?.label || id);
    const primary = topicLabels[0] || "時系列サンプル";
    const phase = SUCCESSOR_CHAPTER_PHASES[index] || `時系列区間${index + 1}`;
    const chapterTitle = successorStyle ? `${phase} — ${primary}` : primary;
    const cutId = `cut_${String(index + 1).padStart(3, "0")}`;
    return {
      cut_id: cutId,
      chapter_id: `chapter_${String(index + 1).padStart(2, "0")}`,
      title: `第${index + 1}章：${chapterTitle}`,
      organization: {
        chronological_phase: phase,
        primary_topic: topics[0]?.[0] || null,
        secondary_topics: topics.slice(1, 3).map(([id]) => id),
        whole_source_slot_index: index + 1,
        whole_source_slot_count: uniformCuts.length,
      },
      source_start_seconds: range.start,
      source_end_seconds: range.end,
      source_caption_event_ids: evidence.map((event) => event.event_id),
      topic_tags: topics.slice(0, 3).map(([id]) => id),
      provenance_type: "source_range_index",
      semantic_status: "machine_indexed_requires_editorial_review",
    };
  });
  return {
    schema_version: "clippipegen.wiki_tensaku_editorial_context.v1",
    artifact_id: artifactId,
    family_id: "miko_led_unofficial_wiki_review",
    source_identity: `youtube:${source.video_id}`,
    expected_selection_mode: "editorial_context_caption_dense_chronological_sampling",
    expected_source_duration_seconds: source.duration_seconds,
    source_duration_basis: sourceDurationBasis,
    source_range_tolerance_seconds: 0.1,
    expected_target_duration_seconds: SLICE_TARGET_SECONDS,
    expected_cut_count: chapters.length,
    chapters,
    creator_commentary: {
      provenance_type: "creator_authored_commentary",
      authority: "ClipPipeGen editorial layer",
      merged_with_source_caption: false,
      events: chapters.map((chapter, index) => ({
        commentary_id: `commentary_${String(index + 1).padStart(3, "0")}`,
        cut_id: chapter.cut_id,
        text: successorStyle
          ? `編集整理「${chapter.organization.chronological_phase}」。${chapter.title.split(" — ").at(-1)}を軸に、公式配信 ${formatTime(chapter.source_start_seconds)}–${formatTime(chapter.source_end_seconds)} を配置した章であり、source captionの発話引用ではない。`
          : `${chapter.title}。公式配信 ${formatTime(chapter.source_start_seconds)}–${formatTime(chapter.source_end_seconds)} の索引範囲。`,
        evidence_caption_event_ids: chapter.source_caption_event_ids,
        provenance_type: "creator_authored_commentary",
        source_caption_claim: false,
      })),
    },
    separation_contract: {
      source_caption_provenance_type: "source_caption",
      creator_commentary_provenance_type: "creator_authored_commentary",
      identifiers_disjoint: true,
      presentation_merged: false,
    },
  };
}

function buildRightsManifest(first, observedAt) {
  return {
    schema_version: "v1",
    episode_id: "wiki_tensaku_family_20260804",
    created_at: observedAt,
    updated_at: observedAt,
    source_video: {
      url: first.url,
      platform: "youtube",
      title: first.title,
      channel: first.channel,
      channel_id: first.channel_id,
      vod_status: first.availability === "OK" ? "public_observed" : "unavailable_observed",
      membership_only: false,
      is_archived_live: first.archived_livestream,
      uploaded_at: first.upload_timestamp,
      duration_seconds: first.duration_seconds,
    },
    talents: [],
    third_party_ip: [],
    prohibited_assets: [],
    required_disclosures: [{ kind: "source_link", text: `元動画: ${first.url}` }],
    publication_constraints: {
      monetization_allowed: false,
      platforms_allowed: [],
      internal_diagnostic_only: true,
    },
    compliance_check: {
      status: "readback_unresolved",
      checked_at: observedAt,
      checked_by: "agent:public_metadata_readback",
      errors: [],
      warnings: ["Public availability is not production/public/monetized permission."],
      review_version: "wiki_tensaku_corpus_v1",
    },
  };
}

async function androidPlayer(videoId, html) {
  const { apiKey } = pageConfig(html);
  const response = await fetch(`https://www.youtube.com/youtubei/v1/player?key=${apiKey}`, {
    method: "POST",
    headers: {
      "user-agent": "com.google.android.youtube/20.10.38 (Linux; U; Android 13)",
      "content-type": "application/json",
      "x-youtube-client-name": "3",
      "x-youtube-client-version": ANDROID_CLIENT.clientVersion,
    },
    body: JSON.stringify({
      context: { client: ANDROID_CLIENT },
      videoId,
      contentCheckOk: true,
      racyCheckOk: true,
    }),
  });
  if (!response.ok) throw new Error(`Android player request failed: ${response.status}`);
  return response.json();
}

async function downloadSelectedSource(source, html, outputDir, observedAt) {
  const mediaDir = join(outputDir, "materials", source.video_id);
  const mediaPath = join(mediaDir, "source_video.mp4");
  const receiptPath = join(mediaDir, "acquisition_receipt.json");
  await mkdir(mediaDir, { recursive: true });
  if (existsSync(mediaPath) && existsSync(receiptPath)) {
    const receipt = JSON.parse(await readFile(receiptPath, "utf8"));
    const digest = await sha256File(mediaPath);
    if (receipt.source_sha256 === digest) {
      if (!Number(receipt.format?.approx_duration_seconds || 0)) {
        const player = await androidPlayer(source.video_id, html);
        const formats = [...(player.streamingData?.formats || []), ...(player.streamingData?.adaptiveFormats || [])];
        const chosen = formats.find((format) => format.itag === 18 && format.url);
        if (chosen) {
          receipt.format.approx_duration_seconds = Number(chosen.approxDurationMs || 0) / 1000;
          await writeJson(receiptPath, receipt);
        }
      }
      return { mediaPath, receipt, reused: true };
    }
    throw new Error("existing source media does not match acquisition receipt");
  }
  const player = await androidPlayer(source.video_id, html);
  if (player.playabilityStatus?.status !== "OK") {
    await writeJson(join(mediaDir, "acquisition_blocker.json"), {
      schema_version: SCHEMA_VERSION,
      observed_at: observedAt,
      state: "BLOCKED_EXTERNAL_CURRENT_ATTEMPT",
      blocker_code: "YOUTUBE_PUBLIC_ANONYMOUS_PLAYER_REQUIRES_LOGIN",
      provider: "youtube_public_android_player",
      source_url: source.url,
      source_identity: `youtube:${source.video_id}`,
      playability_status: player.playabilityStatus?.status || "UNKNOWN",
      playability_reason: player.playabilityStatus?.reason || null,
      cookies_used: false,
      oauth_used: false,
      source_bytes_acquired: false,
      resume_requirement:
        "fresh anonymous public player access or exact user-provided source bytes for this video ID",
    });
    throw new Error(`source is not playable: ${player.playabilityStatus?.status}`);
  }
  const formats = [...(player.streamingData?.formats || []), ...(player.streamingData?.adaptiveFormats || [])];
  const chosen = formats.find((format) => format.itag === 18 && format.url);
  if (!chosen) throw new Error("combined A/V itag 18 is unavailable");
  const partial = `${mediaPath}.part`;
  await rm(partial, { force: true });
  const response = await fetch(chosen.url, {
    headers: { "user-agent": "com.google.android.youtube/20.10.38 (Linux; U; Android 13)" },
  });
  if (!response.ok || !response.body) throw new Error(`media download failed: ${response.status}`);
  await pipeline(Readable.fromWeb(response.body), createWriteStream(partial));
  await rename(partial, mediaPath);
  const info = await stat(mediaPath);
  const receipt = {
    schema_version: SCHEMA_VERSION,
    acquired_at: observedAt,
    provider: "youtube_public_android_player",
    source_url: source.url,
    source_identity: `youtube:${source.video_id}`,
    format: {
      itag: chosen.itag,
      mime_type: chosen.mimeType,
      width: chosen.width,
      height: chosen.height,
      fps: chosen.fps,
      audio_quality: chosen.audioQuality,
      combined_audio_video: true,
      approx_duration_seconds: Number(chosen.approxDurationMs || 0) / 1000,
    },
    source_byte_size: info.size,
    source_sha256: await sha256File(mediaPath),
    signed_media_url_persisted: false,
    cookies_used: false,
    oauth_used: false,
    rights_status: "readback_unresolved",
    production_public_monetized_upload_approved: false,
  };
  await writeJson(receiptPath, receipt);
  return { mediaPath, receipt, reused: false };
}

async function runExistingCorpusSlice(args, outputDir, observedAt) {
  const inventoryPath = join(outputDir, "corpus_inventory.json");
  const corpusReceiptPath = join(outputDir, "corpus_receipt.json");
  if (!existsSync(inventoryPath) || !existsSync(corpusReceiptPath)) {
    throw new Error("--reuse-inventory requires existing corpus_inventory.json and corpus_receipt.json");
  }
  const corpusInventory = JSON.parse(await readFile(inventoryPath, "utf8"));
  const corpusReceipt = JSON.parse(await readFile(corpusReceiptPath, "utf8"));
  const source = (corpusInventory.videos || []).find((row) => row.video_id === args.selectedVideoId);
  if (!source) throw new Error("selected video is absent from the fixed corpus inventory");
  if (source.availability !== "OK" || source.caption_status !== "fetched") {
    throw new Error("selected inventory source is not fixed as available with captions");
  }
  const captionPath = join(outputDir, "captions", `${source.video_id}.ja.json3`);
  if (!existsSync(captionPath)) throw new Error("selected source caption payload is missing");
  const captionPayload = JSON.parse(await readFile(captionPath, "utf8"));
  const captionDigest = await sha256File(captionPath);
  const captionRows = captionEvents(captionPayload);
  if (!captionRows.length) throw new Error("selected source caption payload has no timed events");

  const liveWatch = await collectWatch(source.video_id, { fetchCaption: false });
  let acquisition = null;
  if (args.downloadSelectedSource) {
    acquisition = await downloadSelectedSource(source, liveWatch.html, outputDir, observedAt);
  }
  const acquiredDuration = Number(acquisition?.receipt?.format?.approx_duration_seconds || 0);
  const sourceForSlice = acquiredDuration > 0
    ? { ...source, duration_seconds: acquiredDuration }
    : source;
  const captionById = new Map([[source.video_id, captionPayload]]);
  const topicIndex = buildTopicIndex([source], captionById);
  const editorialContext = buildEditorialContext(sourceForSlice, captionPayload, {
    artifactId: args.artifactId,
    sourceDurationBasis: acquiredDuration > 0
      ? "provider_combined_format_approx_duration"
      : "fixed_corpus_inventory_duration_seconds",
  });
  const rights = buildRightsManifest(sourceForSlice, observedAt);
  const sourceTopicIndex = topicIndex.sources[0];
  const sliceDir = join(outputDir, "slice_inputs", args.artifactId);
  const sliceReceipt = {
    schema_version: SCHEMA_VERSION,
    artifact_id: args.artifactId,
    family_id: corpusInventory.family_id,
    created_at: observedAt,
    corpus_binding: {
      inventory_path: "corpus_inventory.json",
      inventory_sha256: await sha256File(inventoryPath),
      receipt_path: "corpus_receipt.json",
      receipt_sha256: await sha256File(corpusReceiptPath),
      canonical_inventory_sha256: corpusReceipt.corpus?.canonical_inventory_sha256 || null,
      public_surface_completeness: corpusReceipt.missing_and_private?.completeness_claim || null,
    },
    source: {
      source_identity: `youtube:${source.video_id}`,
      inventory_duration_seconds: source.duration_seconds,
      inventory_full_range_seconds: [0, source.duration_seconds],
      acquired_container_approx_duration_seconds: acquiredDuration || null,
      acquisition_receipt_path: `materials/${source.video_id}/acquisition_receipt.json`,
      source_sha256: acquisition?.receipt?.source_sha256 || null,
      source_byte_size: acquisition?.receipt?.source_byte_size || null,
    },
    source_caption: {
      provenance_type: "source_caption",
      path: `captions/${source.video_id}.ja.json3`,
      sha256: captionDigest,
      timed_event_count: captionRows.length,
      full_source_indexed: true,
    },
    whole_source_index: {
      path: `slice_inputs/${args.artifactId}/topic_index.json`,
      topic_window_count: sourceTopicIndex.topic_windows.length,
      correction_anchor_count: sourceTopicIndex.correction_anchors.length,
      chronology_basis: "source_time_ascending_with_before_after_event_context",
      causal_inference_allowed: false,
    },
    creator_commentary: {
      provenance_type: "creator_authored_commentary",
      path: `slice_inputs/${args.artifactId}/editorial_context.json`,
      event_count: editorialContext.creator_commentary.events.length,
      merged_with_source_caption: false,
      source_caption_claim: false,
    },
    live_availability_readback: liveWatch.receipt,
    rights_status: "readback_unresolved",
    production_public_monetized_upload_approved: false,
  };
  await writeJson(join(sliceDir, "editorial_context.json"), editorialContext);
  await writeJson(join(sliceDir, "rights_manifest.json"), rights);
  await writeJson(join(sliceDir, "topic_index.json"), topicIndex);
  await writeJson(join(sliceDir, "slice_receipt.json"), sliceReceipt);
  await writeJson(join(sliceDir, "live_player_readback.json"), liveWatch.receipt);

  const result = {
    state: "EXISTING_CORPUS_SUCCESSOR_SLICE_INPUTS_READY",
    artifact_id: args.artifactId,
    output_dir: outputDir,
    slice_input_dir: sliceDir,
    selected_source_video_id: source.video_id,
    selected_source_inventory_range_seconds: [0, source.duration_seconds],
    selected_source_media: acquisition?.mediaPath || null,
    selected_source_media_sha256: acquisition?.receipt?.source_sha256 || null,
    selected_source_media_reused: acquisition?.reused || false,
    source_caption_sha256: captionDigest,
    source_caption_event_count: captionRows.length,
    topic_window_count: sourceTopicIndex.topic_windows.length,
    correction_anchor_count: sourceTopicIndex.correction_anchors.length,
  };
  await writeJson(join(outputDir, "collector_runs", `${args.artifactId}.json`), result);
  return result;
}

async function main() {
  const args = parseArgs(process.argv.slice(2));
  if (args.help) {
    console.log(usage());
    return;
  }
  const outputDir = resolve(args.outputDir);
  await mkdir(outputDir, { recursive: true });
  const observedAt = new Date().toISOString();
  if (args.reuseInventory) {
    console.log(JSON.stringify(await runExistingCorpusSlice(args, outputDir, observedAt), null, 2));
    return;
  }

  const streams = await crawlChannelTab({
    url: `${CHANNEL_BASE}/streams`,
    contentType: "LOCKUP_CONTENT_TYPE_VIDEO",
    maxPages: args.maxPages,
  });
  const playlists = await crawlChannelTab({
    url: `${CHANNEL_BASE}/playlists`,
    contentType: "LOCKUP_CONTENT_TYPE_PLAYLIST",
    maxPages: args.maxPages,
  });
  const searches = [];
  for (const query of SEARCH_QUERIES) searches.push(await collectSearchSurface(query));

  const candidates = streams.rows.filter((row) => FAMILY_TITLE_PATTERN.test(row.title));
  const captionById = new Map();
  const watchById = new Map();
  const inventory = [];
  for (const candidate of candidates) {
    const watch = await collectWatch(candidate.id);
    watchById.set(candidate.id, watch);
    if (watch.captionPayload) captionById.set(candidate.id, watch.captionPayload);
    inventory.push({
      video_id: candidate.id,
      url: watch.receipt.url,
      title: watch.receipt.title,
      channel: watch.receipt.channel,
      channel_id: watch.receipt.channel_id,
      publish_timestamp: watch.receipt.publish_timestamp,
      upload_timestamp: watch.receipt.upload_timestamp,
      duration_seconds: watch.receipt.duration_seconds,
      availability: watch.receipt.availability,
      archived_livestream: watch.receipt.archived_livestream,
      caption_status: watch.receipt.caption.status,
      authoritative_surface: `${CHANNEL_BASE}/streams`,
    });
  }
  inventory.sort((left, right) => String(left.publish_timestamp).localeCompare(String(right.publish_timestamp)));

  const surfaceDir = join(outputDir, "surface_receipts");
  const captionDir = join(outputDir, "captions");
  const watchDir = join(outputDir, "watch_receipts");
  await mkdir(surfaceDir, { recursive: true });
  await mkdir(captionDir, { recursive: true });
  await mkdir(watchDir, { recursive: true });
  await writeJson(join(surfaceDir, "channel_streams.json"), { observed_at: observedAt, ...streams });
  await writeJson(join(surfaceDir, "channel_playlists.json"), { observed_at: observedAt, ...playlists });
  await writeJson(join(surfaceDir, "global_search.json"), { observed_at: observedAt, searches });
  for (const item of inventory) {
    await writeJson(join(watchDir, `${item.video_id}.json`), watchById.get(item.video_id).receipt);
    if (captionById.has(item.video_id)) {
      await writeJson(join(captionDir, `${item.video_id}.ja.json3`), captionById.get(item.video_id));
    }
  }

  const officialSearchHits = searches.flatMap((search) => search.rows)
    .filter((row) => row.channel_id === CHANNEL_ID);
  const officialSearchUnique = [...new Map(officialSearchHits.map((row) => [row.id, row])).values()];
  const matchingPlaylists = playlists.rows.filter((row) => PLAYLIST_TITLE_PATTERN.test(row.title));
  const corpusInventory = {
    schema_version: SCHEMA_VERSION,
    observed_at: observedAt,
    family_id: "miko_led_unofficial_wiki_review",
    inclusion_criteria: {
      authoritative_channel_id: CHANNEL_ID,
      authoritative_channel_name: CHANNEL_NAME,
      authoritative_surface: `${CHANNEL_BASE}/streams`,
      title_pattern: FAMILY_TITLE_PATTERN.source,
      availability_requirement: "public watch page observed; non-OK retained with availability state",
    },
    exclusions: {
      unofficial_clip_channels: "excluded from authoritative corpus; retained only in auxiliary search receipt",
      unrelated_investigation_titles: "excluded unless title matches family rule",
    },
    videos: inventory,
  };
  const corpusReceipt = {
    schema_version: SCHEMA_VERSION,
    observed_at: observedAt,
    authoritative_channel: { id: CHANNEL_ID, name: CHANNEL_NAME, url: CHANNEL_BASE },
    streams_surface: {
      pages: streams.pages,
      continuation_requests: streams.continuation_requests,
      pagination_exhausted: streams.pagination_exhausted,
      raw_count: streams.raw_count,
      unique_count: streams.unique_count,
      duplicate_count: streams.duplicate_count,
      canonical_rows_sha256: sha256Canonical(streams.rows),
    },
    playlists_surface: {
      pages: playlists.pages,
      continuation_requests: playlists.continuation_requests,
      pagination_exhausted: playlists.pagination_exhausted,
      unique_count: playlists.unique_count,
      matching_playlist_count: matchingPlaylists.length,
      matching_playlists: matchingPlaylists,
      dedicated_playlist_status: matchingPlaylists.length ? "present" : "not_observed",
      canonical_rows_sha256: sha256Canonical(playlists.rows),
    },
    auxiliary_search_surface: {
      queries: SEARCH_QUERIES,
      page_policy: "one current public result page per query; corroboration only",
      official_raw_hit_count: officialSearchHits.length,
      official_unique_hit_count: officialSearchUnique.length,
      duplicate_count_across_queries: officialSearchHits.length - officialSearchUnique.length,
      official_hits: officialSearchUnique,
    },
    corpus: {
      total: inventory.length,
      available_ok: inventory.filter((row) => row.availability === "OK").length,
      unavailable_observed: inventory.filter((row) => row.availability !== "OK").length,
      duplicate_video_ids: inventory.length - new Set(inventory.map((row) => row.video_id)).size,
      canonical_inventory_sha256: sha256Canonical(inventory),
    },
    missing_and_private: {
      public_surface_missing_rows: streams.pagination_exhausted ? 0 : "unknown",
      private_or_deleted_count: "not_observable_from_public_surface",
      completeness_claim: "complete_for_current_public_authoritative_streams_surface_under_recorded_title_rule",
      non_claim: "does_not_claim_private_deleted_unlisted_or_future_videos_are_absent",
    },
    rerun: usage(),
  };
  const topicIndex = buildTopicIndex(inventory, captionById);
  const selected = args.selectedVideoId
    ? inventory.find((row) => row.video_id === args.selectedVideoId)
    : inventory[0];
  if (!selected || !captionById.has(selected.video_id)) {
    throw new Error("no caption-bearing authoritative family source for first slice");
  }
  let acquisition = null;
  if (args.downloadSelectedSource) {
    acquisition = await downloadSelectedSource(
      selected,
      watchById.get(selected.video_id).html,
      outputDir,
      observedAt,
    );
  }
  const acquiredDuration = Number(acquisition?.receipt?.format?.approx_duration_seconds || 0);
  const selectedForSlice = acquiredDuration > 0
    ? { ...selected, duration_seconds: acquiredDuration }
    : selected;
  const editorialContext = buildEditorialContext(
    selectedForSlice,
    captionById.get(selected.video_id),
    { artifactId: args.artifactId },
  );
  const rights = buildRightsManifest(selectedForSlice, observedAt);
  await writeJson(join(outputDir, "corpus_inventory.json"), corpusInventory);
  await writeJson(join(outputDir, "corpus_receipt.json"), corpusReceipt);
  await writeJson(join(outputDir, "topic_index.json"), topicIndex);
  await writeJson(join(outputDir, "first_slice_editorial_context.json"), editorialContext);
  await writeJson(join(outputDir, "rights_manifest.json"), rights);

  const result = {
    state: streams.pagination_exhausted ? "CORPUS_PUBLIC_SURFACE_INVENTORIED" : "CORPUS_COLLECTOR_CONTINUE",
    output_dir: outputDir,
    corpus_total: inventory.length,
    available_total: inventory.filter((row) => row.availability === "OK").length,
    streams_pages: streams.pages,
    streams_total: streams.unique_count,
    playlists_total: playlists.unique_count,
    dedicated_playlist_status: corpusReceipt.playlists_surface.dedicated_playlist_status,
    first_source_video_id: selected.video_id,
    first_source_media: acquisition?.mediaPath || null,
    first_source_media_sha256: acquisition?.receipt?.source_sha256 || null,
    first_source_media_reused: acquisition?.reused || false,
  };
  await writeJson(join(outputDir, "collector_run.json"), result);
  console.log(JSON.stringify(result, null, 2));
}

function scrubUrl(value) {
  const parsed = new URL(value);
  return `${parsed.protocol}//${parsed.host}${parsed.pathname}`;
}

function round6(value) {
  return Math.round((Number(value) + Number.EPSILON) * 1e6) / 1e6;
}

function roundHalfEven(value) {
  const floor = Math.floor(value);
  const fraction = value - floor;
  if (Math.abs(fraction - 0.5) < 1e-12) return floor % 2 === 0 ? floor : floor + 1;
  return Math.round(value);
}

function formatTime(seconds) {
  const whole = Math.max(0, Math.round(seconds));
  const hours = Math.floor(whole / 3600);
  const minutes = Math.floor((whole % 3600) / 60);
  const rest = whole % 60;
  return [hours, minutes, rest].map((value) => String(value).padStart(2, "0")).join(":");
}

function sha256Text(value) {
  return createHash("sha256").update(String(value), "utf8").digest("hex");
}

function sha256Canonical(value) {
  return sha256Text(JSON.stringify(value));
}

async function sha256File(path) {
  const payload = await readFile(path);
  return createHash("sha256").update(payload).digest("hex");
}

async function writeJson(path, value) {
  await mkdir(dirname(path), { recursive: true });
  await writeFile(path, `${JSON.stringify(value, null, 2)}\n`, "utf8");
}

main().catch((error) => {
  console.error(`wiki-tensaku collector failed: ${error.stack || error.message}`);
  process.exitCode = 2;
});
