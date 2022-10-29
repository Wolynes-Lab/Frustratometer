"""
Unit and regression test for the dca_frustratometer package.
"""

# Import package, test suite, and other packages as needed
import sys
import dca_frustratometer
import numpy as np
import tempfile
from pathlib import Path


def test_download_pfam_database():
    """ This test downloads a small database from pfam and splits the files in a folder"""
    name='pfam_dead'
    url='https://ftp.ebi.ac.uk/pub/databases/Pfam/current_release/Pfam-A.dead.gz'
    path = dca_frustratometer._path
    print(path)
    databases_path = dca_frustratometer.create_directory(path / 'databases')
    alignments_path = dca_frustratometer.download.pfam.database(databases_path, url=url, name=name)
    assert (alignments_path / 'Unknown.sto').exists() is False
    assert (alignments_path / 'PF00065.sto').exists() is True

def test_get_alignment_from_database():
    pass


def test_download_pfam_alignment():
    with tempfile.NamedTemporaryFile(mode="w", prefix="dcaf_", suffix='_interpro.sto') as output_handle:
        output = Path(output_handle.name)
        assert output.exists()
        output_text = output.read_text()
        assert output_text==""
        output = dca_frustratometer.download.pfam.alignment('PF09696',output)
        assert output.exists()
        output_text = output.read_text()
        assert "#=GF AC   PF09696" in output_text
    assert not output.exists()


def test_filter_alignment():
    pass


def test_create_potts_model_from_aligment():
    with tempfile.NamedTemporaryFile(mode="w", prefix="dcaf_", suffix='_interpro.sto') as alignment_file,\
         tempfile.NamedTemporaryFile(mode="w", prefix="dcaf_", suffix='_filtered.fa') as filtered_file:
        dca_frustratometer.download_alignment_from_interpro("PF09696", alignment_file.name)
        dca_frustratometer.filter_alignment(alignment_file.name, filtered_file.name)
        potts_model = dca_frustratometer.create_pottsmodel_from_alignment_pydca(filtered_file.name)
    assert 'h' in potts_model.keys()
    assert 'J' in potts_model.keys()

def test_create_potts_model_from_pdb():
    pass


def test_dca_frustratometer_imported():
    """Sample test, will always pass so long as import statement worked."""
    assert "dca_frustratometer" in sys.modules

def test_identify_pfamID():
    pfamID = dca_frustratometer.get_pfamID("6U5E","A")
    assert pfamID=="PF00160"

def test_aligment_filtration():
    alignment_file = dca_frustratometer.generate_alignment(pdb_name="5MSM_B",pfamID="PF09696")
    filtered_alignment_file = dca_frustratometer.convert_and_filter_alignment(alignment_file)
    assert filtered_alignment_file.exists()

def test_functional_compute_native_energy():
    seq = dca_frustratometer.get_protein_sequence_from_pdb('examples/data/1cyo.pdb', 'A')
    distance_matrix = dca_frustratometer.get_distance_matrix_from_pdb('examples/data/1cyo.pdb', 'A')
    potts_model = dca_frustratometer.load_potts_model('examples/data/PottsModel1cyoA.mat')
    mask = dca_frustratometer.compute_mask(distance_matrix, distance_cutoff=4, sequence_distance_cutoff=0)
    e = dca_frustratometer.compute_native_energy(seq, potts_model, mask)
    assert np.round(e, 4) == -61.5248


def test_OOP_compute_native_energy():
    pdb_file = 'examples/data/1cyo.pdb'
    chain = 'A'
    potts_model_file = 'examples/data/PottsModel1cyoA.mat'
    model = dca_frustratometer.PottsModel.from_potts_model_file(potts_model_file, pdb_file, chain, distance_cutoff=4,
                                                                sequence_cutoff=0)
    e = model.native_energy()
    assert np.round(e, 4) == -61.5248


def test_scores():
    pdb_file = 'examples/data/1cyo.pdb'
    chain = 'A'
    potts_model_file = 'examples/data/PottsModel1cyoA.mat'
    model = dca_frustratometer.PottsModel.from_potts_model_file(potts_model_file, pdb_file, chain, distance_cutoff=4,
                                                                sequence_cutoff=0)
    assert np.round(model.scores()[30, 40], 5) == -0.02234


def test_compute_singleresidue_decoy_energy():
    aa_x = 5
    pos_x = 30
    distance_cutoff = 4
    sequence_cutoff = 0
    distance_matrix = dca_frustratometer.get_distance_matrix_from_pdb('examples/data/1cyo.pdb', 'A')
    potts_model = dca_frustratometer.load_potts_model('examples/data/PottsModel1cyoA.mat')
    seq = dca_frustratometer.get_protein_sequence_from_pdb('examples/data/1cyo.pdb', 'A')
    mask = dca_frustratometer.compute_mask(distance_matrix, distance_cutoff, sequence_cutoff)
    AA = '-ACDEFGHIKLMNPQRSTVWY'
    seq = [aa for aa in seq]
    seq[pos_x] = AA[aa_x]
    seq = ''.join(seq)
    test_energy = dca_frustratometer.compute_native_energy(seq, potts_model, mask)
    decoy_energy = dca_frustratometer.compute_decoy_energy(seq, potts_model, mask, 'singleresidue')
    assert (decoy_energy[pos_x, aa_x] - test_energy) ** 2 < 1E-16


def test_compute_mutational_decoy_energy():
    aa_x = 5
    pos_x = 30
    aa_y = 7
    pos_y = 69
    distance_cutoff = 4
    sequence_cutoff = 0
    distance_matrix = dca_frustratometer.get_distance_matrix_from_pdb('examples/data/1cyo.pdb', 'A')
    potts_model = dca_frustratometer.load_potts_model('examples/data/PottsModel1cyoA.mat')
    seq = dca_frustratometer.get_protein_sequence_from_pdb('examples/data/1cyo.pdb', 'A')
    mask = dca_frustratometer.compute_mask(distance_matrix, distance_cutoff, sequence_cutoff)
    AA = '-ACDEFGHIKLMNPQRSTVWY'
    seq = [aa for aa in seq]
    seq[pos_x] = AA[aa_x]
    seq[pos_y] = AA[aa_y]
    seq = ''.join(seq)
    test_energy = dca_frustratometer.compute_native_energy(seq, potts_model, mask)
    decoy_energy = dca_frustratometer.compute_decoy_energy(seq, potts_model, mask, 'mutational')
    assert (decoy_energy[pos_x, pos_y, aa_x, aa_y] - test_energy) ** 2 < 1E-16
