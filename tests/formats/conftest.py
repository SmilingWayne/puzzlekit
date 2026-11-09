import pytest


@pytest.fixture
def puzzlink_test_urls():
    """Puzzlink cases"""
    return {
        # Heyawake
        "heyawake_1": "https://puzz.link/p?heyawake/10/10/ckpbir56acsk19mjc63grjo33g0cvv1vo37og2g31j1g221i33k2g",
        "heyawake_2_mark?": "https://puzz.link/p?heyawake/10/10/ckpbir56acsk19mjc63grjo33g0cvv1vo37og2g31j1g22.i33k2g",
        "heyawake_3": "https://puzz.link/p?heyawake/20/20/00000i805541aaa2kkkdp94riaa74kse99osijh8n72hef32pq43j48464g8890gg4gk0310000007s00ov0300o07o04o0s30v0f7s2000000000vv00000fo1s8fs2007o7g0400003vvo0s3007s00411g53g2j9i844h1j5g2g6g63g5h",
        
        # shimaguni
        "shimaguni_1": "https://puzz.link/p?shimaguni/10/10/884aha5h85jshipgi17vjqfmudt1buhlti1ui2h34g3m",
        
        # aqre
        "aqre_1": "https://puzz.link/p?aqre/12/6/4i2914gi8944i000001vvg000057711373",
        "aqre_2": "https://puzz.link/p?aqre/12/12/1aglaa552i01h0oic944i2954ig007vs000fvvv007o01vgfg3s00033332361g2g1g17416414",
        
        # nonogram
        "nonogram_1": "https://puzz.link/p?nonogram/15/15/22l33l1221j231k251k11l9m311k272k2212j21511i12321i2112j21l22l3m12l222k1211j152k211113h21122i2112j21122i211113h252k1321j222k132k3",
        "nonogram_2": "https://puzz.link/p?nonogram/12/12/1k3k5k1k1k11j71j1k1k1k1k1k1k2kck2k1k2k1k1k1k1k1k1k",
        "nonogram_3": "https://puzz.link/p?nonogram/15/11/55j111i13p55j1k55j1k121i5111h12j5k121i21111g1212h33113i111111h11113i11111i3331r111111h211211h22111i111111h211113h",
        "nonogram_4": "https://puzz.link/p?nonogram/13/14/3l33k412j252j124j44k411j4111i45kbl231j611j33k2l211j133j224j162j421j44k411j214j124j82k62k7l3l",
        
        # ayeheya
        "ayeheya_1": "https://puzz.link/p?ayeheya/16/13/930930920920920cgg4gg4gg4gg4gg489489489000c0vo7g0000fvvs00007o000001vvv0000000254l5h45g453g",
        "ayeheya_2": "https://puzz.link/p?ayeheya/11/10/5i5ililkkkkhkh4h444400e003se0ov00e00vs00g2k2n",
        
        # stostone
        "stostone_1": "https://puzz.link/p?stostone/6/6/g0iic2vn03ecg3255g",
        "stostone_2": "https://puzz.link/p?stostone/12/10/0000000000000000002000007vu00fvvvv007vu0vvo0gccc6g",
        
        # kurotto
        "kurotto_1": "https://puzz.link/p?kurotto/10/10/h42j4m.g1h...2g.g.o5i12r1.i4o1g1g3.33h2g.m5j13h",
        "kurotto_2": "https://puzz.link/p?kurotto/10/10/.l7l3g1g.g6g2n1h2h1o6h8g3har06.h6zh3h./",
        
        # kurochute
        "kurochute_1": "https://puzz.link/p?kurochute/14/8/1i7l32g2h4g1j6h13i2j1i24l2k35k5l46i4j3i57h2j6g2h6g43l1i7",
        
        # kurodoko
        "kurodoko_1": "https://puzz.link/p?kurodoko/9/9/3j4h3l.l4j8p4i2p2j4l.l3h3j2",
        "kurodoko_2": "https://puzz.link/p?kurodoko/20/10/j7m3l5g6i6p5k4i5l4i8k4l7i4i8g3l6i9i9n5i4i3l5g5i2i4l3k6i2l5i6kap2i5gelem2j",
        
        # nurimisaki
        "nurimisaki_1": "https://puzz.link/p?nurimisaki/10/10/4g.i.h3t.n3j.v3zk.k3h.i.k",
        "nurimisaki_2": "https://puzz.link/p?nurimisaki/10/10/5i4n4j.n.j2g3j3s5g2v.g3s4n7h",
        
        # nurikabe
        "nurikabe_1": "https://puzz.link/p?nurikabe/10/10/h5k7t6l5p2h4p2g2q4g7j2v3j2g",
        "nurikabe_2": "https://puzz.link/p?nurikabe/10/10/j2m3i2i2h.j6t4k..k3t6j.h4i4i2m2j",
        
        # masyu
        "masyu_1": "https://puzz.link/p?mashu/14/8/330000096960006ik00039a00010j0i0000220",
        "masyu_2": "https://puzz.link/p?mashu/10/15/39000c0966103093ibf40d3262003j31008060003l03990030",
        "masyu_3": "https://puzz.link/p?masyu/10/10/0000909b360200013a3a39000i063j1010",
        
        # slitherlink
        "slitherlink_1": "https://puzz.link/p?slither/18/10/gbcg2dgddd73d28ddw2307612185132bicjcnbjai3318712387333dwb62d16dbdbg1cgca",
        "slitherlink_2": "https://puzz.link/p?slither/5/6/2bgb0bbhb1adg1b",
        
        # vslither
        "vslither_1" : "https://puzz.link/p?vslither/7/7/766ck776ek789ek976b",
        
        # tslither
        "tslither_1": "https://puzz.link/p?tslither/6/11/2cgbg3d1bgdg2c3d2cgcg3d2cgbg2c2c2cgc",
        
        # country road
        "countryroad_1": "https://puzz.link/p?country/12/16/jp7vd1633018180c0606gdkckcjvnjuvt410a5jag780410280o000141mgmfjmnc20gg3bum-4am35g16h",
        
        # yajilin
        "yajilin_1": "https://puzz.link/p?yajilin/20/5/o32c21b22a43u43d34r21zc",
        "yajilin_2": "https://puzz.link/p?yajilin/9/11/j21a11b40y21a33k21a41y11b31a13j",
        
        # castle
        "castle_1": "https://puzz.link/p?castle/6/6/e032a241h20.b00.h131a042e",
        "castle_2": "https://puzz.link/p?castle/10/10/022022f032022d00.00.t03200.c04200.j00.012c00.032p01200.d042012m032012a",
        
        # hebi (snakes)
        "hebi_1": "https://puzz.link/p?hebi/10/10/n150.15a42a41b320.c0.a0.0.d310.0.b240.n230.b0.0.42d0.0.a0.c0.21b0.a21a0.0.0.n",
        "hebi_2": "https://puzz.link/p?hebi/7/10/i13k2544d15t15d14d44b43h",
        
        # test url parse 
        "url_parse_1": "https://puzz.link/p?stostone/6/6/4hcudmf5re4i4k3",
        "url_parse_2": "https://puzz.link/p?slither/10/10/b86ag68dg127bg62aldg8dad8bgdl26dg722cg68dg88bd",
        "url_parse_3": "http://pzv.jp/p?yajilin/17/17/q41i21a232323l21y30111111v41b41za2041r41b41u4141414141j21h32a32b32z1242s21b21k32g42124214141412j",
        "url_parse_4": "https://pzplus.tck.mn/p?heyawake/18/10/2i58kha5495929aagaik2kl4l5959a86qi00001ofvo0003vuc006e3v07hg01pvvo04324i53i222h322i12g1l",
        
        # tapa
        "tapa_1": "https://puzz.link/p?tapa/16/11/r2j7galafg.....s0n5i5ha0ga0a0a0h2na0ia0ma8ia0g8gb0g7h3la0ia0l4h8ga0g..a0g8q.g.k4gabgalgabg.0.g3q.k",
        "tapa_2": "https://puzz.link/p?tapa/9/9/o2iajadh5lajm5k4l4k7g44g3q4l1ha7h",
        "tapa_3": "https://puzz.link/p?tapa/8/8/1g4h2g.n1la9j4l4j2la8n.gaeh3g./",
        
        # tapa-like-loop
        "tapalikeloop_1": "https://puzz.link/p?tapaloop/11/9/uasg+2ulark+2us2j+47j3saikakl8gaku",
        "tapalikeloop_2": "https://puzz.link/p?tapaloop/10/10/qa0h.i+10j.qa0k+10q.a0h.a0v-10i.ga0ia0m.ia0h",
        
        # fillomino
        "fillomino_1": "https://puzz.link/p?fillomino/10/10/h343i3o2g434h2h1l1g3j3h2g5j5g5h4j2g3l4h5h344g3o4i434h",
        "fillomino_2": "https://puzz.link/p?fillomino/18/10/3h6i3245i3h6h4h25j42h6i4h25l23h4g3i5h3144h1i42h3h3j2h3h41h2h5j2h3h34i4h3443h5i5g5h14l63h5i1h15j33h5h4h5i6436i1h6",
    }