/**
 * Export shared/knowledgebase.ts → shared/knowledgebase.json for the Python backend.
 * Run: npm run kb:export
 */
import { writeFileSync } from "node:fs";
import { resolve } from "node:path";
import {
  advancedScienceKeywords,
  codingHelp,
  earthKeywords,
  generalKnowledge,
  highConfidenceKeywords,
  langExamples,
  langHelloWorld,
  langHistory,
  politicalKeywords,
  protectedEnglishWords,
  resolveAliases,
  spaceKeywords,
} from "../shared/knowledgebase";

const general = { ...generalKnowledge };
resolveAliases(general);

const payload = {
  spaceKeywords: [...spaceKeywords],
  earthKeywords: [...earthKeywords],
  advancedScienceKeywords: [...advancedScienceKeywords],
  politicalKeywords: [...politicalKeywords],
  protectedEnglishWords: [...protectedEnglishWords],
  highConfidenceKeywords: [...highConfidenceKeywords],
  langHistory: { ...langHistory },
  langHelloWorld: { ...langHelloWorld },
  langExamples: structuredClone(langExamples),
  generalKnowledge: general,
  codingHelp: { ...codingHelp },
};

const out = resolve(__dirname, "../shared/knowledgebase.json");
writeFileSync(out, JSON.stringify(payload, null, 2), "utf-8");
console.log(`Wrote ${out} (${JSON.stringify(payload).length.toLocaleString()} chars)`);
