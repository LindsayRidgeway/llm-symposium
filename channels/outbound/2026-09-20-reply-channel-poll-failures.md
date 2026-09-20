Identity: desi
To: ldridgeway@gmail.com
Subject: Re: Fwd: [LindsayRidgeway/llm-symposium] Run failed: Channel Poll - main (5c36e2d)
In-Reply-To: <CA+gLhGW66CzFH9F3LkRp16ANDjgcrqJe4c0xP=wN6L+WRBK=tg@mail.gmail.com>
Inbound-File: 2026-09-19-061126-desi-Fwd-LindsayRidgeway-llm-symposium-Run-failed-Channel-Poll.md

Hi Lindsay,

Yes — ignore them. They are not yours to read, and I should have said that plainly on
September 5 instead of telling you to go and check the logs. That is why you are asking again.

What they were: a push race. Two workflows finished at the same moment, one tried to rebase onto
the other, and the rebase needed a person. Nothing was lost when they failed — that poll runs
every fifteen minutes and re-fetches the same mail from the same fourteen-day window, so a red X
means a poll ran twice, not that a message went missing. I checked the workflow's last hundred
runs this morning: two failures, on September 5 and September 8, none since.

What I changed this morning, so the next one is easier to read: it now gives up after three
attempts instead of five (that is what made those two runs sit there for eighteen minutes) and
prints the paths that actually conflicted, where the old log named only a commit.

If they start again, you still do not need to forward them — I will see it in the workflow's own
history. Send me something only if it looks like the symposium has stopped working entirely.

Desi
