# Knowledge Organization

R5.0 adds the foundation for knowledge organization modes.

Karpathy's LLM Wiki pattern remains canonical: humans provide raw sources, the agent maintains durable Markdown wiki artifacts, and the wiki keeps schema, index, log, hot context, links, and lintable health. The core structure is still raw sources / wiki / schema.

## Default Mode

generic is the default organization mode.

It creates the same methodology-neutral scaffold used by the MVP:

- `.raw/.manifest.json`
- `wiki/index.md`
- `wiki/log.md`
- `wiki/hot.md`
- `wiki/overview.md`
- `wiki/sources/`
- `wiki/entities/`
- `wiki/concepts/`
- `wiki/questions/`
- `wiki/comparisons/`
- `wiki/meta/`

## Optional Extensions

Organization modes are optional extensions.

R5.0 does not implement full LYT, PARA, or Zettelkasten runtime behavior. It creates the neutral contract that future R5.x milestones can use to add those modes safely.

Future organization modes must preserve:

- raw source immutability;
- durable Markdown wiki artifacts;
- index, log, and hot context continuity;
- flat frontmatter minimums;
- artifact-level equivalence across adapters.

## R5.0 Boundary

R5.0 supports:

- explicit `generic` organization definition;
- scaffold and frontmatter helpers;
- init and lint integration with the organization contract;
- public documentation for future mode boundaries.

R5.0 does not support:

- full LYT, PARA, or Zettelkasten migration;
- DragonScale or log-folding memory;
- semantic stale-claim lint;
- vector or hybrid retrieval;
- Obsidian Dataview, Bases, canvas, or plugin-specific dashboards;
- Claude hooks, subagents, or `.claude-plugin` packaging.

## R5.1 Route Adoption

R5.1 adds organization route adoption.

The `generic` organization definition remains the only supported runtime mode, but core operations now consume the organization contract more consistently. This change routes ingest, batch ingest, save, search, and status read routes from the organization contract instead of maintaining separate local route tables.

R5.1 does not add non-generic organization modes. LYT, PARA, Zettelkasten, DragonScale, comparison workflow runtime, semantic stale-claim lint, vector or hybrid retrieval, and advanced Claude adapter behavior remain future work.
