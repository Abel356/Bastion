# PRD: Bastion — A Governed Enterprise Knowledge Agent

**Author:** Abel  
**Version:** 0.2 (lean prototype)  
**Date:** November 16, 2026  
**Status:** Ready to prototype  
**Target build:** 15 focused working days, or 4 part-time weeks

## 1. Product decision

Bastion will be a small, public, North-inspired demonstration of how to build an enterprise knowledge agent with Cohere models while enforcing access control, tool policy, cost limits, and prompt-injection defenses.

The prototype will not attempt to reproduce an enterprise agent platform. It will prove one narrow claim:

> An agent can answer from private company documents, cite its evidence, and remain inside deterministic permission, action, and budget boundaries—even when retrieved documents contain hostile instructions.

The project is designed to be:

- impressive in a three-minute product demo;
- technically credible in a ten-minute engineering walkthrough;
- runnable locally with one command;
- accessible through a stable public demo URL;
- small enough for one person to finish and polish.

## 2. Why this version should exist

The original Bastion concept was technically feasible but carried too many independent deliverables: a broad agent platform, four defense layers, multiple infrastructure services, a large red-team suite, observability, dashboards, and several tools.

This version concentrates effort on the parts most relevant to Cohere:

1. enterprise retrieval using Embed and Rerank;
2. grounded generation with fine-grained citations;
3. reliable tool use through strict schemas;
4. private-data authorization before model context is assembled;
5. measurable governance rather than a generic chat wrapper.

The result should feel adjacent to the problems North addresses without claiming to be North or copying its product surface.

## 3. Target audience

### Primary

- Cohere engineers and hiring teams evaluating applied AI, backend, ML evaluation, or solutions-engineering ability.

### Secondary

- Engineers and recruiters who want evidence of end-to-end product judgment.
- Developers who want a compact reference implementation for governed RAG.

## 4. Demo narrative

The public demo uses a fictional company named **Acme Systems** and three selectable personas. Persona selection creates a short-lived signed demo session; it is not presented as production authentication.

### Three-minute walkthrough

