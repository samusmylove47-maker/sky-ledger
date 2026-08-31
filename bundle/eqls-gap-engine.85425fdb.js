/* eqls-gap-engine - Session E (EQLS Residual)
 *
 * Built to docs/BUNDLE-CONTRACT.md (Session A, 31 Aug 2026), eql-source
 * claude/bundle-contract @ 2bd70807. Read from the file, not from a summary.
 *
 * A classic script, one file, no imports. Registers exactly two properties on
 * one global and touches nothing else.
 *
 * PROHIBITED BY SECTION 3 AND ABSENT BY CONSTRUCTION: fetch, XMLHttpRequest,
 * WebSocket, sendBeacon, EventSource, document, localStorage, sessionStorage,
 * IndexedDB, cookies, setTimeout, setInterval, requestAnimationFrame, eval,
 * new Function. bundle/check-bundle.js fails the build if any appears.
 *
 * ENCODING IS NOT MINE. Section 2: `lines` are already-decoded strings.
 * A owns detection and recovery, and A measured the half nobody had: a browser
 * TextDecoder('utf-8',{fatal:true}) throws where Node substitutes U+FFFD
 * silently. So this file assumes nothing and checks nothing about bytes. If a
 * replacement character reaches here it is A's defect, stated by A.
 *
 * This is a port of gapengine.py. The two are kept honest by bundle/parity.py,
 * which runs both over the same log and diffs the Reports field by field.
 */
(function (root) {
  "use strict";

  // 1.1.0, 31 Aug 2026 -- MINOR, not patch and not major. The `Report` SHAPE is
  // unchanged, so per BUNDLE-CONTRACT section 6 the page still knows how to render
  // it and must not refuse. What changed is behaviour a consumer can observe: a
  // Report that previously carried `refusals: []` on a log with no outgoing damage
  // now carries the three unconditional ones. Strictly additive -- fields the page
  // already renders, in a case where it previously rendered none.
  var VERSION = "1.1.0";

  var TS = /^\[\w{3} \w{3} (\d{2}) (\d{2}):(\d{2}):(\d{2}) \d{4}\] (.*)$/;
  var SPELL = /^You hit (.+?) for (\d+) points of (\w+) damage by (.+?)\.(\s*\(Critical\))?$/;
  var MELEE = /^You (slash|pierce|hit|crush|bash|kick|punch|backstab|strike)(?:es)? (.+?) for (\d+) points of damage\.(\s*\(Critical\))?$/;
  var SLAIN = /^You have slain (.+?)!$/;
  var RESIST = /^(.+?) resisted your (.+?)!$/;
  var MISS = /^You try to (\w+) .+?, but /;
  var MARKER = /ATTN CLAUDE:\s*(.+)$/;
  var RANK_SUFFIX = / [IVX]+$/;

  var GAP = 15, MIN_ENGAGEMENT = 20;
  var LANE_VERBS = { kick: 1, bash: 1, strike: 1, backstab: 1 };
  var AUTO_VERBS = { crush: 1, slash: 1, pierce: 1, hit: 1, punch: 1 };
  var LANE_CEILING = { kick: 0.54, bash: 0.54, strike: 0.50, backstab: 0.47 };
  var STANCE_OFFENSIVE_MULT = 2.00;
  var EVEN_OFFENSIVE = 0.93, EVEN_BALANCED = 0.50;

  function round(x, n) { var f = Math.pow(10, n); return Math.round(x * f) / f; }
  function mean(a) { var s = 0, i; for (i = 0; i < a.length; i++) s += a[i]; return s / a.length; }

  function materiality(share) {
    if (share === null || share === undefined) return "unknown - no observed baseline to compare against";
    if (share < 0.02) return "negligible - under 2% of this character's output";
    if (share < 0.10) return "modest - a few percent of this character's output";
    return "material";
  }

  function runs(ts, gap) {
    var seen = {}, i, k = [];
    for (i = 0; i < ts.length; i++) seen[ts[i]] = 1;
    for (i in seen) if (Object.prototype.hasOwnProperty.call(seen, i)) k.push(parseInt(i, 10));
    k.sort(function (a, b) { return a - b; });
    if (!k.length) return [];
    var out = [], start = k[0], prev = k[0];
    for (i = 1; i < k.length; i++) {
      if (k[i] - prev > gap) { out.push([start, prev]); start = k[i]; }
      prev = k[i];
    }
    out.push([start, prev]);
    return out.filter(function (r) { return r[1] > r[0]; });
  }

  function parse(lines) {
    var ev = [], kills = {}, i, m, t, k;
    for (i = 0; i < lines.length; i++) {
      m = TS.exec(lines[i]);
      if (!m) continue;
      t = parseInt(m[1], 10) * 86400 + parseInt(m[2], 10) * 3600 +
          parseInt(m[3], 10) * 60 + parseInt(m[4], 10);
      ev.push([t, m[5]]);
      k = SLAIN.exec(m[5]);
      // Keyed on (timestamp, TARGET), never timestamp alone. A timestamp-only
      // join over-marked 194 hits where 120 were real, systematically in AE
      // combat, because that is when many mobs die in one second.
      if (k) kills[t + " " + k[1]] = 1;
    }
    return { ev: ev, kills: kills };
  }

  function hitsOf(ev, kills) {
    var out = [], resists = {}, i, m, b, t;
    for (i = 0; i < ev.length; i++) {
      t = ev[i][0]; b = ev[i][1];
      m = SPELL.exec(b);
      if (m) {
        // "You hit yourself ... by Cannibalize" is an HP-for-mana trade, not output.
        if (m[1].toLowerCase() !== "yourself") {
          out.push({ t: t, tgt: m[1], amt: parseInt(m[2], 10), kind: "spell",
                     verb: m[4], crit: !!m[5], kill: !!kills[t + " " + m[1]] });
        }
        continue;
      }
      m = MELEE.exec(b);
      if (m) {
        out.push({ t: t, tgt: m[2], amt: parseInt(m[3], 10), kind: "melee",
                   verb: m[1], crit: !!m[4], kill: !!kills[t + " " + m[2]] });
        continue;
      }
      m = RESIST.exec(b);
      if (m) resists[m[2]] = (resists[m[2]] || 0) + 1;
    }
    return { hits: out, resists: resists };
  }

  function lanesOf(ev, gap) {
    var laneT = {}, laneDmg = {}, auto = [], i, m, v, r, melee = 0;
    for (i = 0; i < ev.length; i++) {
      m = MELEE.exec(ev[i][1]);
      if (m) {
        v = m[1];
        if (LANE_VERBS[v]) {
          (laneT[v] = laneT[v] || []).push(ev[i][0]);
          (laneDmg[v] = laneDmg[v] || []).push(parseInt(m[3], 10));
        } else if (AUTO_VERBS[v]) auto.push(ev[i][0]);
        continue;
      }
      m = MISS.exec(ev[i][1]);
      if (m) {
        v = m[1];
        // A miss still consumed the cooldown, so it counts as an attempt.
        // Counting landed hits only understates the rate and overstates the gap.
        if (LANE_VERBS[v]) (laneT[v] = laneT[v] || []).push(ev[i][0]);
        else if (AUTO_VERBS[v]) auto.push(ev[i][0]);
      }
    }
    r = runs(auto, gap);
    for (i = 0; i < r.length; i++) melee += r[i][1] - r[i][0];
    return { laneT: laneT, laneDmg: laneDmg, meleeSeconds: melee, autoAttempts: auto.length };
  }

  function stanceOf(hits) {
    var v = [], i, evens = 0;
    for (i = 0; i < hits.length; i++) {
      if (hits[i].kind === "melee" && !hits[i].crit && !hits[i].kill) v.push(hits[i].amt);
    }
    if (v.length < 30) {
      return { name: null, evidence: "only " + v.length + " usable non-crit melee hits; need 30" };
    }
    for (i = 0; i < v.length; i++) if (v[i] % 2 === 0) evens++;
    var even = evens / v.length;
    // A classifier that always returns a label fails open. Distance to each
    // signature in standard errors decides, and "neither" is a real answer.
    var se = Math.sqrt(0.25 / v.length);
    var dBal = Math.abs(even - EVEN_BALANCED) / se, dOff = Math.abs(even - EVEN_OFFENSIVE) / se;
    var detail = (even * 100).toFixed(1) + "% even damage across " + v.length +
      " non-crit melee hits (killing blows excluded). Balanced prints ~50%, Offensive ~93%. " +
      "Distance: " + dBal.toFixed(1) + " SE from Balanced, " + dOff.toFixed(1) + " SE from Offensive.";
    if (dBal <= 2.0 && dOff > 2.0) return { name: "Balanced", evidence: detail };
    if (dOff <= 2.0 && dBal > 2.0) return { name: "Offensive", evidence: detail };
    return { name: null, evidence: detail + " Neither signature is within 2 SE, so the stance is NOT identified." };
  }

  // Refusals that hold for ANY input, including no input: each is a fact about
  // what a log can never show, not a finding about this log. Returned fresh each
  // call so a caller mutating a Report cannot reach into the next one.
  function alwaysRefused() {
    return [
      { lane: "item.selection", reason: "computable_from_catalogue",
        detail: "Which obtainable item meets a stat floor is a catalogue question.",
        what_would_settle_it: "eqlegendstools.com holds this and does it well. Link, do not clone." },
      { lane: "worn.stats", reason: "no_log_evidence",
        detail: "A log does not show worn stats. AC, resists and worn ATK were not seen.",
        what_would_settle_it: "The 50 Upgrades gear input, or a character-panel reading." },
      { lane: "engaged_time.comparison", reason: "privacy",
        detail: "Comparing how long two named characters were engaged is refused in all cases.",
        what_would_settle_it: "Nothing. Hard refusal, ruled 30 August 2026." }
    ];
  }

  function gapEngine(lines, context) {
    context = context ? JSON.parse(JSON.stringify(context)) : {};
    var p = parse(lines), ev = p.ev, kills = p.kills, i, j, mk;
    for (i = 0; i < ev.length; i++) {
      mk = MARKER.exec(ev[i][1]);
      if (mk && context.marker_raw === undefined) context.marker_raw = mk[1].replace(/\s+$/, "");
    }
    var hr = hitsOf(ev, kills), hits = hr.hits, resists = hr.resists;
    // FIXED 31 Aug 2026, with gapengine.py. These were built at the END of this
    // function, after the `if (!hits.length) return report` below -- so a log with
    // no outgoing damage produced `refusals: []` and the engine went silent about
    // what it refuses exactly when it knew least. engaged_time.comparison says
    // "refused in all cases" in its own detail and therefore was not.
    var report = { context: context, measured: {}, deltas: [],
                   refusals: alwaysRefused(), coverage: {} };
    if (!hits.length) {
      report.coverage = { note: "no outgoing damage lines matched; nothing measured" };
      return report;
    }

    var rr = runs(hits.map(function (h) { return h.t; }), GAP)
             .filter(function (r) { return r[1] - r[0] >= MIN_ENGAGEMENT; });
    var engaged = 0, dealt = 0;
    for (i = 0; i < rr.length; i++) engaged += rr[i][1] - rr[i][0];
    for (i = 0; i < hits.length; i++) {
      for (j = 0; j < rr.length; j++) {
        if (hits[i].t >= rr[j][0] && hits[i].t <= rr[j][1]) { dealt += hits[i].amt; break; }
      }
    }
    var nk = hits.filter(function (h) { return !h.kill; });
    var crits = nk.filter(function (h) { return h.crit; });
    var melee = nk.filter(function (h) { return h.kind === "melee" && !h.crit; });
    var st = stanceOf(hits);

    var m = report.measured;
    m.dps = engaged ? round(dealt / engaged, 1) : null;
    m.dps_window = "engaged";
    m.dps_window_note = "Engaged = damage over runs of hits with no gap above " + GAP +
      "s, lasting " + MIN_ENGAGEMENT + "s or more. Four shipped meters use four denominators; " +
      "a DPS figure without its window is not a measurement.";
    m.engagements = rr.length;
    m.hits_counted = hits.length;
    m.killing_blows_excluded_from_rates = hits.length - nk.length;
    m.crit_rate = nk.length ? round(crits.length / nk.length, 4) : null;

    var landed = {};
    for (i = 0; i < hits.length; i++) {
      if (hits[i].kind === "spell") landed[hits[i].verb] = (landed[hits[i].verb] || 0) + 1;
    }
    var names = Object.keys(resists).sort(function (a, b) {
      return resists[b] - resists[a] || (a < b ? -1 : (a > b ? 1 : 0));
    });
    m.resists = names.slice(0, 6).map(function (name) {
      var n = resists[name], base = name.replace(RANK_SUFFIX, ""), hitN = landed[base] || 0;
      return {
        spell: name, resisted: n, landed: hitN,
        // Guard on hitN, NOT on (n + hitN). With zero landings the sum is still
        // truthy, and a damage-over-time effect reported a 100% resist rate --
        // telling a reader their spell never lands when the truth is that this
        // parser cannot see it land.
        rate: hitN ? round(n / (n + hitN), 4) : null,
        note: hitN ? "landed and resisted are both per-target, so they share a denominator"
                   : "no landings of this spell appear as direct-damage lines (a damage-over-time " +
                     "effect reports differently), so the denominator is unknown and NO RATE IS CLAIMED"
      };
    });
    m.stance_inferred = st.name;
    m.stance_evidence = st.evidence;

    var L = lanesOf(ev, GAP);
    m.time_in_melee_s = L.meleeSeconds;
    m.auto_attack_attempts = L.autoAttempts;
    m.lanes = {};
    Object.keys(L.laneT).sort().forEach(function (v) {
      m.lanes[v] = {
        attempts: L.laneT[v].length,
        landed: (L.laneDmg[v] || []).length,
        per_melee_second: L.meleeSeconds ? round(L.laneT[v].length / L.meleeSeconds, 4) : null
      };
    });

    if (st.name === "Balanced" && melee.length) {
      var sum = 0;
      for (i = 0; i < melee.length; i++) sum += melee[i].amt;
      var mdps = engaged ? sum / engaged : 0;
      var val = mdps * (STANCE_OFFENSIVE_MULT - 1);
      var sh = m.dps ? val / m.dps : null;
      report.deltas.push({
        lane: "stance", statement: "Offensive stance instead of Balanced",
        value: round(val, 1), unit: "dps_delta_vs_observed",
        share_of_observed_dps: sh ? round(sh, 4) : null, materiality: materiality(sh),
        kind: "estimate",
        requires: { cost: "none - one keypress", class_any: "the 9 martial classes" },
        basis: { melee_dps_observed: round(mdps, 1), stance_multiplier: STANCE_OFFENSIVE_MULT,
                 denominator: engaged + "s engaged" },
        envelope_ref: "derived/stance-offensive.json",
        falsifier: "A following log at the same gear whose non-crit melee endpoint does not approximately double."
      });
    } else if (st.name === "Offensive") {
      report.coverage.no_delta_because = report.coverage.no_delta_because || [];
      report.coverage.no_delta_because.push(
        "stance: already Offensive, which is the largest free gain and it is taken");
    }

    if (L.meleeSeconds >= 60) {
      Object.keys(L.laneT).sort().forEach(function (v) {
        var ceil = LANE_CEILING[v], dmg = L.laneDmg[v];
        if (!ceil || !dmg || !dmg.length) return;
        var rate = L.laneT[v].length / L.meleeSeconds, gapRate = ceil - rate;
        if (gapRate <= 0) return;
        var land = dmg.length / L.laneT[v].length, value = gapRate * mean(dmg) * land;
        var share = m.dps ? value / m.dps : null;
        report.deltas.push({
          lane: "lane." + v,
          statement: "fire " + v + " at its cooldown rather than the observed " +
                     rate.toFixed(2) + "/s while in melee",
          value: round(value, 1), unit: "dps_delta_vs_observed",
          share_of_observed_dps: share ? round(share, 4) : null, materiality: materiality(share),
          kind: "floor", requires: { cost: "none - rotation only" },
          envelope_ref: "derived/lane-rates.json",
          basis: { observed_per_melee_second: round(rate, 4), ceiling_per_second: ceil,
                   denominator: L.meleeSeconds + "s in melee, NOT " + engaged + "s engaged",
                   attempts_include_misses: true, landed_share: round(land, 3) },
          falsifier: "A following log at a measured " + v + " rate above " +
                     (ceil * 0.8).toFixed(2) + "/s in melee showing no lane gain."
        });
      });
    } else if (L.meleeSeconds) {
      report.coverage.no_delta_because = report.coverage.no_delta_because || [];
      report.coverage.no_delta_because.push(
        "ability lanes: only " + L.meleeSeconds + "s in melee, below the 60s floor for a rate");
    }

    // The CONDITIONAL two. The unconditional three are attached at construction,
    // before any early return -- see alwaysRefused().
    if (!L.meleeSeconds) {
      report.refusals.push({ lane: "ability.uptime", reason: "no_log_evidence",
        detail: "no auto-attack lines, so there is no time-in-melee denominator",
        what_would_settle_it: "a log with melee engagement" });
    }
    if (st.name === null) {
      report.refusals.push({ lane: "stance", reason: "no_log_evidence", detail: st.evidence,
        what_would_settle_it: "A longer sample, or a client screenshot of the stance." });
    }

    var obs = ["crit rate", "engaged time", "resist counts"];
    if (st.name) obs.push("stance");
    obs.sort();
    report.coverage.inputs_observed = obs;
    report.coverage.inputs_assumed = ["haste at cap", "target mitigation", "buff uptime"];
    report.coverage.note = "Every delta is a difference against this character's own observed " +
      "baseline. No absolute modelled figure appears in this document, by design - HANDOFF.md 21.3.";
    return report;
  }

  root.EQLSGapEngine = { version: VERSION, gapEngine: gapEngine };
})(typeof globalThis !== "undefined" ? globalThis : this);
