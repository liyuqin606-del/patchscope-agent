# Evidence desk design

Audience: engineers reviewing experiment results and recruiters inspecting a reproducible demo.
Task: compare conditions, inspect rejected correct candidates, see cost and evidence limitations.

- Color: warm paper `#f4f2ec`, ink `#202720`, muted green `#657065`, structural lines `#ccd0c5`.
  Deep green marks controls; rust marks false rejections. No success color is used to imply correctness.
- Typography: Georgia editorial headings and body; Menlo for quantities, labels and system status.
- Layout: wide report desk, two-column comparison/context, single-column narrow breakpoint at 700px.
- Components: experiment selector, explicit refresh, denominator table, expandable raw case records,
  error/loading states. No API call controls, credentials or arbitrary filesystem paths.
