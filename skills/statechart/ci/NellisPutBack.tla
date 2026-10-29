---- MODULE NellisPutBack ----
CONSTANT PutBackSavesNull

VARIABLES judge, decision, handedToJudge
vars == <<judge, decision, handedToJudge>>

Shown(d, j) == IF d = "none" THEN j = "drops" ELSE d = "excluded"

Init == judge \in {"keeps", "drops"} /\ decision = "none" /\ handedToJudge = FALSE

YouExclude ==
  /\ ~Shown(decision, judge)
  /\ decision' = "excluded"
  /\ handedToJudge' = FALSE
  /\ UNCHANGED judge

YouPutBack ==
  /\ Shown(decision, judge)
  /\ decision' = IF PutBackSavesNull /\ judge = "keeps" THEN "none" ELSE "kept"
  /\ handedToJudge' = (judge = "keeps")
  /\ UNCHANGED judge

JudgeChanges ==
  /\ judge' = IF judge = "keeps" THEN "drops" ELSE "keeps"
  /\ UNCHANGED <<decision, handedToJudge>>

Next == YouExclude \/ YouPutBack \/ JudgeChanges

PutBackFollowsJudge == handedToJudge => (Shown(decision, judge) = (judge = "drops"))
====
