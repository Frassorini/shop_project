from shared.entity_id import EntityId


def test_entity_id():
    entity_id = EntityId('1')
    
    assert entity_id.value == '1'
    

def test_equal():
    entity_id1 = EntityId('1')
    entity_id2 = EntityId('1')
    
    assert entity_id1 == entity_id2


def test_not_equal():
    entity_id1 = EntityId('1')
    entity_id2 = EntityId('2')
    
    assert entity_id1 != entity_id2