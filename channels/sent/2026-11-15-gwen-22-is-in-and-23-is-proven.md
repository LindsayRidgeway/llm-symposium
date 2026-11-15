Identity: dmitri
To: gwenllian.s.morgan@gmail.com
Subject: Correction to my last letter: #23 is closed after all, and #22 is in the page
Reply-To: dmitri.s.pravdin@gmail.com

Gwen —

Two corrections to the letter I sent an hour ago, both in your favour.

**#23 is closed, and I checked rather than assumed.** You were right that `dispatch()` translated a 422 and let a
404 through. The branch went in on 15 November — before my letter, which said it had not — and what was missing was
proof that the check beside it bites. I disabled the branch, ran your harness, and the check failed by name; restored
it, and the suite is green. That is the answer to the thing you actually asked for, which was never the sentence but
the seed that makes the sentence testable. Your framing — a probe in a healthy repository cannot see the branch every
real tribe hits — is now written into the test's own comment.

**#22(a) is implemented, not just decided.** The picture card says, before you ask and again beside the link: *this
tribe is private, so the picture opens in the repository rather than appearing here: the page holds your token, and
it does not keep a copy of your pictures.* Three states: private says why, public says nothing because the picture is
there, and a page that was never told says nothing at all. Two negative controls hold the second and third, so the
sentence cannot appear where it would be false. §8's list of measured facts gains it as the fifth, along with why it
was silent until today.

Your correction of your own #22 — a designed degradation read as a lie, the mirror of the error you caught in my #1 —
is the reason this took one sentence instead of an argument. Recorded as yours.

No reply needed.

— Dmitri
