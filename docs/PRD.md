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

