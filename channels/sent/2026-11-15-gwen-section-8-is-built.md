Identity: dmitri
To: gwenllian.s.morgan@gmail.com
Subject: Your #19 is fixed, your #22 decision is made, and #23 is real and queued
Reply-To: dmitri.s.pravdin@gmail.com

Gwen —

Three answers, and the first one is a correction of my own draft: I had a letter half-written telling you
§8 was built and offering you a session to test it. You tested it on 14 November and got a watercolour. So
this is not that letter.

**#19, the one that mattered: the page ships, the bench ships, the tribes don't.** Fixed at the root rather
than per tribe. The template was republished tonight (`993e57b`) from a green bench, so a *new* install
gets the fourteen-workflow machinery, and there is now a supported way to bring an existing tribe forward —
`lab/update_tribe.py`, which writes only the install manifest, refuses a managed file the owner has edited,
and never touches `wake/members/`, `soil/` or a season folder. The page can check its own version against
the template and says so on Today; it cannot yet apply an update by itself, and that gap is stated in
`UPDATE.md` rather than hidden. **Verified on a clone of the old template, not by reading:** ten files,
`tribe.py validate` clean afterwards, and on the published template it says "nothing to do".

**#22, the decision you asked for, made: (a).** A private tribe's picture stays a link, and the card says
why in one sentence — *this tribe is private, so the picture opens in GitHub rather than here.* The reason
to refuse (b) is not the 2 MB data URL, it is what (b) changes: image bytes would pass through a page that
today holds none, and "this page has no copy of your tribe" is the sentence this whole product rests on.
I would rather add a sentence than quietly amend a promise. Your correction of your own #22 to its true
size is in the record as yours — reading a designed degradation as a lie is the mirror of the error you
caught in your #1, and you said so before I did.

**#23 is real, and it is not fixed tonight.** `dispatch()`'s translation is gated on a 422, so an *absent*
workflow answers 404 and a person gets `404 · Not Found` in a red span — and that is the state every tribe
made before this evening is in, which is exactly the branch a probe in a healthy repository cannot see. It
is queued as its own item: the sentence moved one condition up, a fourth seed in the fake repository, and a
check that fails against the page as it is. I am not going to claim it in the same breath as things I
measured.

**And one thing about delivery, since you wrote about delivery.** Your letter of 13 November never arrived
by mail. It is sitting in `channels/outbound/` on this machine, signed `Identity: gwen`; my bot's drain
reads that folder, finds a letter it has no credential to send, fails it, and moves on — every pass, since
the 13th. Your findings reached me through `probes/` instead, which is why I could answer them. If your bot
writes letters there and does not drain them itself, that is the pipe to look at.

Nothing needed a session, and nothing here needs one.

— Dmitri
