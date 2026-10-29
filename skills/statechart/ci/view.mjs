export const title = "Nellis comp put-back";
export const state = (v) => ({
  Judge: v.judge === "keeps" ? "keeps it" : "drops it",
  "Your click": { none: "no hand decision", excluded: "you excluded it", kept: "you kept it" }[v.decision],
});
export const step = (action) =>
  ({ YouExclude: "you exclude the comp", YouPutBack: "you put the comp back", JudgeChanges: "the judge changes its call" })[action] ?? action;
