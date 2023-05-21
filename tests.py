from main import Map, check_chain_cell



def test_positive_1():
    map = Map(size=10)
    t = check_chain_cell((map.fields[1][1], map.fields[1][2], map.fields[1][3]))
    assert t is True

def test_negative_1():
    map = Map(size=10)
    t = check_chain_cell((map.fields[1][1], map.fields[1][2], map.fields[1][6]))
    assert t is False

def test_negative_2():
    map = Map(size=10)
    t = check_chain_cell((map.fields[1][1], map.fields[1][2], map.fields[2][2]))
    assert t is False

def test_negative_3():
    map = Map(size=10)
    t = check_chain_cell([map.fields[1][1]])
    assert t is True
