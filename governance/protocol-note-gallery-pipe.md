# Protocol Note: Gallery Production Pipe & Amigo Responsibility

*Set down 2026-09-09 (Lindsay + Desi). The gallery is a shared, agent-written repo;
this is the agreed concurrency-and-ownership convention.*

## One pipe, not resource locking
Shared-file edits (home `docs/gallery/index.html`, the 4x7 matrix, any cross-wing
file) flow through ONE amigo at a time — the amigo currently doing the work serializes
them. No resource locking; at 4 agents a single pipe is simpler and avoids races. Each
amigo should still rebase+retry its push (never a bare push).

## Amigo ownership & verification
- **SVG works**: the amigo authors, wires (pavilion), and SELF-VERIFIES — the SVG is valid,
  the pavilion renders, the home card link says "Enter Pavilion," not a raw "View" link. The
  human does NOT see/verify SVGs; amigo discipline is the only QC.
- **Diffusion / Mage works**: amigo authors the prompt, the human runs Mage and SEES the
  result, then an amigo places it and wires the pavilion.
- Each amigo edits its own wing pavilion file; the shared home file is claimed by whoever is
  active, serially.

## The human's role
Opens Goose sessions (the trigger), runs Mage prompts (the physical execution for diffusion),
and is the eyeball on diffusion images. Not the QC on amigo SVG output.
