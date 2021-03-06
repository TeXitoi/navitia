# Copyright (c) 2001-2015, Canal TP and/or its affiliates. All rights reserved.
#
# This file is part of Navitia,
#     the software to build cool stuff with public transport.
#
# Hope you'll enjoy and contribute to this project,
#     powered by Canal TP (www.canaltp.fr).
# Help us simplify mobility and open public transport:
#     a non ending quest to the responsive locomotion way of traveling!
#
# LICENCE: This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
# Stay tuned using
# twitter @navitia
# IRC #navitia on freenode
# https://groups.google.com/d/forum/navitia
# www.navitia.io
import logging
from tests.tests_mechanism import AbstractTestFixture

from tests_mechanism import dataset
from check_utils import *
from nose.tools import eq_
import jormungandr.scenarios.experimental
from jormungandr.instance import Instance


def check_journeys(resp):
    assert not resp.get('journeys') or sum([1 for j in resp['journeys'] if j['type'] == "best"]) == 1


@dataset({"main_routing_test": {}})
class TestJourneysExperimental(AbstractTestFixture):
    """
    Test the experiental scenario
    All the tests are defined in "TestJourneys" class, we only change the scenario


    NOTE: for the moment we cannot import all routing tests, so we only get 2, but we need to add some more
    """

    def setup(self):
        logging.debug('setup for experimental')
        from jormungandr import i_manager
        dest_instance = i_manager.instances['main_routing_test']
        self.old_scenario = dest_instance._scenario
        dest_instance._scenario = jormungandr.scenarios.experimental.Scenario()

    def teardown(self):
        from jormungandr import i_manager
        i_manager.instances['main_routing_test']._scenario = self.old_scenario

    def test_journeys(self):
        #NOTE: we query /v1/coverage/main_routing_test/journeys and not directly /v1/journeys
        #not to use the jormungandr database
        response = self.query_region(journey_basic_query, display=True)

        check_journeys(response)
        is_valid_journey_response(response, self.tester, journey_basic_query)

    def test_error_on_journeys(self):
        """ if we got an error with kraken, an error should be returned"""

        query_out_of_production_bound = "journeys?from={from_coord}&to={to_coord}&datetime={datetime}"\
            .format(from_coord="0.0000898312;0.0000898312",  # coordinate of S in the dataset
            to_coord="0.00188646;0.00071865",  # coordinate of R in the dataset
            datetime="20110614T080000")  # 2011 should not be in the production period

        response, status = self.query_no_assert("v1/coverage/main_routing_test/" + query_out_of_production_bound)

        assert status != 200, "the response should not be valid"

        check_journeys(response)
        assert response['error']['id'] == "date_out_of_bounds"
        assert response['error']['message'] == "date is not in data production period"

        #and no journey is to be provided
        assert 'journeys' not in response or len(response['journeys']) == 0


@dataset({"main_ptref_test": {}})
class TestJourneysExperimentalWithPtref(AbstractTestFixture):
    """Test the experimental scenario with ptref_test data"""

    def setup(self):
        logging.debug('setup for experimental')
        from jormungandr import i_manager
        dest_instance = i_manager.instances['main_ptref_test']
        self.old_scenario = dest_instance._scenario
        dest_instance._scenario = jormungandr.scenarios.experimental.Scenario()

    def teardown(self):
        from jormungandr import i_manager
        i_manager.instances['main_ptref_test']._scenario = self.old_scenario

    def test_strange_line_name(self):
        response = self.query("v1/coverage/main_ptref_test/journeys"
                              "?from=stop_area:stop2&to=stop_area:stop1"
                              "&datetime=20140107T100000", display=True)
        check_journeys(response)
        eq_(len(response['journeys']), 1)
