# coding=utf-8

import numpy
import pytest

from PyPWA.libs import configuration_db
from PyPWA.libs.math import particle


@pytest.fixture(scope="function", autouse=True)
def clear_configuration():
    with pytest.warns(RuntimeWarning):
        configuration_db.Connector().purge()


def make_new_vector_array():
    vector = numpy.zeros(500, particle.NUMPY_PARTICLE_DTYPE)
    vector['x'] = numpy.random.rand(500)
    vector['y'] = numpy.random.rand(500)
    vector['z'] = numpy.random.rand(500)
    vector['e'] = numpy.random.rand(500)
    return vector


def make_new_particle(geant_id):
    charge = numpy.random.choice([-1, 0, 1])
    return particle.Particle(geant_id, charge, make_new_vector_array())


def make_new_particle_pool():
    new_particle_pool = []
    for geant_id in [1, 3, 4, 7, 13]:
        new_particle_pool.append(make_new_particle(geant_id))

    return particle.ParticlePool(new_particle_pool)


@pytest.fixture(scope="module")
def random_particle_pool():
    return make_new_particle_pool()