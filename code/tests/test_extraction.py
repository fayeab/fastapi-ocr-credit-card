import os
import sys
import cv2
rep_file = os.path.dirname(__file__)
app_dir = os.path.join(rep_file, '..', 'app')
sys.path.append(app_dir)
from extraction import extract_infos_carte

def test_extractions_visa():
    """
    Tests 
    """
    # Test avec une carte Visa
    path_image = 'files/carte_visa.jpg'
    image = cv2.imread(path_image)
    res_attendu = {'carte_num': '4970101234567890', 'carte_type': 'Visa'}
    res_obtenu = extract_infos_carte(image)
    print(res_obtenu)
    assert res_obtenu == res_attendu

def test_extractions_mastercard():
    """
    Tests 
    """
    # Test avec une carte Mastercard
    path_image = 'files/carte_mastercard.jpg'
    image = cv2.imread(path_image)
    res_attendu = {'carte_num': '5412153456189123', 'carte_type': 'MasterCard'}
    res_obtenu = extract_infos_carte(image)
    assert res_obtenu == res_attendu
