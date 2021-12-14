# Script recorded by TexGen v3.12.0

weave = CTextileWeave2D(3, 2, 1.1, 0.23, bool(1), bool(1))
weave.SetGapSize(0)

weave.SetYarnWidths(0.81)
weave.SetXYarnWidths(0, 0.81)
weave.SetXYarnHeights(0, 0.115)
weave.SetXYarnSpacings(0, 1.1)

weave.SetXYarnWidths(1, 0.81)
weave.SetXYarnHeights(1, 0.115)
weave.SetXYarnSpacings(1, 1.1)
weave.SetYYarnWidths(0, 0.81)
weave.SetYYarnHeights(0, 0.115)
weave.SetYYarnSpacings(0, 1.1)
weave.SetYYarnWidths(1, 0.81)
weave.SetYYarnHeights(1, 0.115)
weave.SetYYarnSpacings(1, 1.1)
weave.SetYYarnWidths(2, 0.81)
weave.SetYYarnHeights(2, 0.115)
weave.SetYYarnSpacings(2, 1.1)
weave.AssignDefaultDomain()
textilename = AddTextile(weave)

