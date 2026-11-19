# Adapter roadmap

The following puzzles are candidates for the next adapters. Their puzz.link
URL types are present in the merged link collection and have a dispatcher in
the pinned cspuz backend. A successful backend sample does **not** mean that
PuzzleKit's FileIO and state support is complete, or that every variant is
compatible. Each puzzle still needs its own pzpr verification.

The first group is a suggested development order: begin with cell and room
shading, then extend loop and number-answer support.

1. Minesweeper (`mines`)
2. Choco Banana (`cbanana`)
3. Yin-Yang (`yinyang`)
4. Ekawayeh (Symmetry Heyawake) (`ayeheya`)
5. Shimaguni (`shimaguni`)
6. Chocona (`chocona`)
7. Stostone (`stostone`)
8. Simple Loop (`simpleloop`)
9. Country Road (`country`)
10. Yajilin (Regions) (`yajilin-regions`)
11. Fillomino (`fillomino`)
12. Sudoku (`sudoku`)

<details>
<summary>More candidates, in suggested order</summary>

After the first group, these candidates are ordered by the availability of
sample links. Order is a planning aid and may change after compatibility and
implementation checks.

13. Shakashaka (`shakashaka`)
14. Double Choco (`dbchoco`)
15. Sashigane (`sashigane`)
16. Firefly (`firefly`)
17. Nurimaze (`nurimaze`)
18. Slalom (`slalom`)
19. Tapa (`tapa`)
20. Yajisan-Kazusan (`yajikazu`)
21. Slant (`gokigen`)
22. Reflect Link (`reflect`)
23. Kakuro (`kakuro`)
24. Tasquare (`tasquare`)
25. School Trip (`shugaku`)
26. Herugolf (`herugolf`)
27. Moon or Sun (`moonsun`)
28. Fivecells (`fivecells`)
29. Castle Wall (`castle`)
30. Hebi-Ichigo (`hebi`)
31. Paintarea (`paintarea`)
32. Curve Data (`curvedata`)
33. Hashiwokakero (`hashi`)
34. Ring-Ring (`ringring`)
35. Barns (`barns`)
36. Pencils (`pencils`)
37. Chained Block (`chainedb`)
38. Geradeweg (`geradeweg`)
39. Ripple Effect (`ripple`)
40. Sukoro (`sukoro`)
41. Snake (`snake`)
42. Nanro (`nanro`)
43. Compass (`compass`)
44. Kropki (`kropki`)
45. Detour (`detour`)
46. Guide Arrow (`guidearrow`)
47. Statue Park (`statuepark`)
48. Akichiwake (`akichi`)
49. Tents (`tents`)
50. Aquarium (`aquarium`)
51. Putteria (`putteria`)
52. Rail Pool (`railpool`)
53. Koburin (`koburin`)
54. Nagenawa (`nagenawa`)
55. Cocktail Lamp (`cocktail`)
56. Easy as ABC (`easyasabc`)
57. Skyscrapers (`skyscrapers`)
58. Araf (`araf`)
59. Ice Walk (`icewalk`)
60. Heteromino (`heteromino`)
61. Double Back (`doubleback`)
62. Pentominous (`pentominous`)
63. Square Jam (`squarejam`)
64. La Paz (`lapaz`)
65. NIKOJI (`nikoji`)
66. Fourcells (`fourcells`)
67. Circles and Squares (`circlesquare`)
68. Light and Shadow (`lightshadow`)
69. Nonogram (`nonogram`)
70. Army Ants (`armyants`)
71. Kouchoku (`kouchoku`)
72. Loop Special (`loopsp`)
73. Roma (`roma`)
74. Lohkous (`lohkous`)
75. Dominion (`dominion`)
76. Fillmat (`fillmat`)
77. Evolmino (`evolmino`)
78. Aquapelago (`aquapelago`)
79. Canal View (`canal`)
80. Context (`context`)
81. Coral (`coral`)
82. Yajisan-Sokoban (`yajisoko`)
83. Litherslink (`lither`)
84. No Three (`nothree`)
85. Tontonbeya (`tontonbeya`)
86. Bosanowa (`bosanowa`)
87. Nanameguri (`nanameguri`)
88. Norinuri (`norinuri`)
89. Cross the Streams (`cts`)
90. Tetrochain Y (`tetrochain`)
91. Forest Walk (`forestwalk`)
92. Water Walk (`waterwalk`)
93. Firewalk (`firewalk`)
94. Slash Pack (`slashpack`)
95. Coffee Milk (`coffeemilk`)
96. Key West (`keywest`)
97. Kurarin (`kurarin`)
98. Mintonette (`mintonette`)
99. Simple Gako (`simplegako`)
100. Tile City (`tilecity`)
101. All or Nothing (`nothing`)
102. Battleship (`battleship`)

</details>

Two other cspuz dispatch entries need investigation before joining this list:
Building Walk (`bdwalk`), whose sampled links were rejected by the upstream
URL decoder, and Balloon Box (`balloon`), whose sampled solve timed out. A
timeout is not a no-solution result.
