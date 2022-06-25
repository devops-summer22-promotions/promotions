# Copyright 2016, 2019 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Test Factory to make fake objects for testing
"""
import factory
from datetime import date
from factory.fuzzy import FuzzyChoice, FuzzyDate
from service.models import Promotion, PromoType


class PromoFactory(factory.Factory):
    """Creates fake promotions with dummy name to be overridden in tests"""

    class Meta:  # pylint: disable=too-few-public-methods
        """Maps factory to data model"""

        model = Promotion

    id = factory.Sequence(lambda n: n)
    name = "PLACEHOLDER" # replace during testing
    type = FuzzyChoice(choices=[PromoType.BUY_ONE_GET_ONE, PromoType.PERCENT_DISCOUNT, PromoType.FREE_SHIPPING, PromoType.VIP])
    discount = None # placeholder; override during testing
    customer = None # placeholder; override during testing
    start_date = FuzzyDate(date(2022, 7, 1), date(2022, 7, 31))
    end_date = FuzzyDate(date(2022, 10, 1), date(2022, 10, 31))
