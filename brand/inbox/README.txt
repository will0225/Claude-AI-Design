# Drop downloaded files here

Save or copy anything you download into this folder:
  - meeting notes (.txt)
  - exported data (.csv)
  - copied web content (.txt, .md)
  - research notes (.txt)

Then run ONE command:

  cd python
  python make.py proposal    ← newest inbox file → your proposal template
  python make.py report      ← newest inbox file → your report template

The layout, fonts, colors, and section order are always the same.
Only the content changes based on what you dropped in.

Tip: rename files if you want a specific one processed:
  python make.py proposal --file ../brand/inbox/my-file.txt

Processed files move to inbox/done/ automatically.
