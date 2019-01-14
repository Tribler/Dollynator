import copy
import unittest
import mock
import cloudomate.hoster.vps.blueangelhost as blueAngel
from CaseInsensitiveDict import CaseInsensitiveDict

from cloudomate.hoster.vps.vps_hoster import VpsOption
from mock import MagicMock

from plebnet.agent.qtable import QTable, VPSState, ProviderOffer
from plebnet.controllers import cloudomate_controller


class TestQTable(unittest.TestCase):
    qtable = {}
    providers = {}
    option = {}

    @mock.patch('plebnet.controllers.cloudomate_controller.get_vps_providers',
                return_value=CaseInsensitiveDict({'blueangelhost': blueAngel.BlueAngelHost}))
    @mock.patch('plebnet.controllers.cloudomate_controller.options', return_value=[VpsOption(name='Advanced',
                                                                                             storage=2,
                                                                                             cores=2,
                                                                                             memory=2,
                                                                                             bandwidth="mock",
                                                                                             connection="1",
                                                                                             price=100.0,
                                                                                             purchase_url="mock"
                                                                                             ),
                                                                                   VpsOption(name='Basic Plan',
                                                                                             storage=2,
                                                                                             cores=2,
                                                                                             memory=2,
                                                                                             bandwidth="mock",
                                                                                             connection="1",
                                                                                             price=10.0,
                                                                                             purchase_url="mock"
                                                                                             )])
    def setUp(self, mock1, mock2):
        self.qtable = QTable()
        self.providers = cloudomate_controller.get_vps_providers()

    def tearDown(self):
        del self.qtable
        del self.providers

    @mock.patch('plebnet.controllers.cloudomate_controller.get_vps_providers',
                return_value=CaseInsensitiveDict({'blueangelhost': blueAngel.BlueAngelHost}))
    @mock.patch('plebnet.controllers.cloudomate_controller.options', return_value=[VpsOption(name='Advanced',
                                                                                             storage=2,
                                                                                             cores=2,
                                                                                             memory=2,
                                                                                             bandwidth="mock",
                                                                                             connection="1",
                                                                                             price=100.0,
                                                                                             purchase_url="mock"
                                                                                             ),
                                                                                   VpsOption(name='Basic Plan',
                                                                                             storage=2,
                                                                                             cores=2,
                                                                                             memory=2,
                                                                                             bandwidth="mock",
                                                                                             connection="1",
                                                                                             price=10.0,
                                                                                             purchase_url="mock"
                                                                                             )])
    def test_init_providers(self, mock1, mock2):
        assert (len(self.qtable.providers_offers) == 0)

        self.qtable.init_providers_offers(self.providers)
        assert (len(self.qtable.providers_offers) > 0)

    @mock.patch('plebnet.controllers.cloudomate_controller.get_vps_providers',
                return_value=CaseInsensitiveDict({'blueangelhost': blueAngel.BlueAngelHost}))
    @mock.patch('plebnet.controllers.cloudomate_controller.options', return_value=[VpsOption(name='Advanced',
                                                                                             storage=2,
                                                                                             cores=2,
                                                                                             memory=2,
                                                                                             bandwidth="mock",
                                                                                             connection="1",
                                                                                             price=100.0,
                                                                                             purchase_url="mock"
                                                                                             ),
                                                                                   VpsOption(name='Basic Plan',
                                                                                             storage=2,
                                                                                             cores=2,
                                                                                             memory=2,
                                                                                             bandwidth="mock",
                                                                                             connection="1",
                                                                                             price=10.0,
                                                                                             purchase_url="mock"
                                                                                             )])
    def test_init_qtable_and_environment(self, mock1, mock2):
        assert (len(self.qtable.environment) == 0)
        self.qtable.init_qtable_and_environment(self.providers)
        assert (len(self.qtable.environment) > 0)
        assert (len(self.qtable.qtable) > 0)

    @mock.patch('plebnet.controllers.cloudomate_controller.get_vps_providers',
                return_value=CaseInsensitiveDict({'blueangelhost': blueAngel.BlueAngelHost}))
    @mock.patch('plebnet.controllers.cloudomate_controller.options', return_value=[VpsOption(name='Advanced',
                                                                                             storage=2,
                                                                                             cores=2,
                                                                                             memory=2,
                                                                                             bandwidth="mock",
                                                                                             connection="1",
                                                                                             price=100.0,
                                                                                             purchase_url="mock"
                                                                                             ),
                                                                                   VpsOption(name='Basic Plan',
                                                                                             storage=2,
                                                                                             cores=2,
                                                                                             memory=2,
                                                                                             bandwidth="mock",
                                                                                             connection="1",
                                                                                             price=10.0,
                                                                                             purchase_url="mock"
                                                                                             )])
    def test_calculate_measure(self, mock1, mock2):
        provider_offer = ProviderOffer(provider_name="mock provider", name="mock name", bandwidth=3, price=5, memory=2)
        assert (self.qtable.calculate_measure(provider_offer) == 0.006)

    @mock.patch('plebnet.controllers.cloudomate_controller.get_vps_providers',
                return_value=CaseInsensitiveDict({'blueangelhost': blueAngel.BlueAngelHost}))
    @mock.patch('plebnet.controllers.cloudomate_controller.options', return_value=[VpsOption(name='Advanced',
                                                                                             storage=2,
                                                                                             cores=2,
                                                                                             memory=2,
                                                                                             bandwidth="mock",
                                                                                             connection="1",
                                                                                             price=100.0,
                                                                                             purchase_url="mock"
                                                                                             ),
                                                                                   VpsOption(name='Basic Plan',
                                                                                             storage=2,
                                                                                             cores=2,
                                                                                             memory=2,
                                                                                             bandwidth="mock",
                                                                                             connection="1",
                                                                                             price=10.0,
                                                                                             purchase_url="mock"
                                                                                             )])
    def test_calculate_measure_unmetric_bandwidth(self, mock1, mock2):
        self.qtable.init_qtable_and_environment(self.providers)
        assert (self.qtable.calculate_measure(self.qtable.providers_offers[0]) == 0.001)

    @mock.patch('plebnet.controllers.cloudomate_controller.get_vps_providers',
                return_value=CaseInsensitiveDict({'blueangelhost': blueAngel.BlueAngelHost}))
    @mock.patch('plebnet.controllers.cloudomate_controller.options', return_value=[VpsOption(name='Advanced',
                                                                                             storage=2,
                                                                                             cores=2,
                                                                                             memory=2,
                                                                                             bandwidth="mock",
                                                                                             connection="1",
                                                                                             price=100.0,
                                                                                             purchase_url="mock"
                                                                                             ),
                                                                                   VpsOption(name='Basic Plan',
                                                                                             storage=2,
                                                                                             cores=2,
                                                                                             memory=2,
                                                                                             bandwidth="mock",
                                                                                             connection="1",
                                                                                             price=10.0,
                                                                                             purchase_url="mock"
                                                                                             )])
    def test_update_environment_positive(self, mock1, mock2):
        blue_angel_offers = cloudomate_controller.options(self.providers["blueangelhost"])
        self.qtable.self_state = VPSState("blueangelhost", blue_angel_offers[0].name)
        self.qtable.init_qtable_and_environment(self.providers)
        environment_copy = copy.deepcopy(self.qtable.environment)
        vps_options_list = cloudomate_controller.options(self.providers)
        vps_option = vps_options_list[0]

        provider_offer_ID = str(self.providers.keys()[0]).lower() + "_" + str(vps_option.name).lower()
        provider_offer_ID_other = str(self.providers.keys()[0]).lower() + "_" + str(vps_options_list[1].name).lower()

        self.qtable.update_environment(provider_offer_ID, True)
        assert (environment_copy != self.qtable.environment)
        assert (environment_copy[provider_offer_ID_other][provider_offer_ID_other] ==
                self.qtable.environment[provider_offer_ID_other][provider_offer_ID_other])
        assert (environment_copy[provider_offer_ID][provider_offer_ID] <
                self.qtable.environment[provider_offer_ID][provider_offer_ID])
        assert(self.qtable.environment[provider_offer_ID][provider_offer_ID] == 0.4)

    @mock.patch('plebnet.controllers.cloudomate_controller.get_vps_providers',
                return_value=CaseInsensitiveDict({'blueangelhost': blueAngel.BlueAngelHost}))
    @mock.patch('plebnet.controllers.cloudomate_controller.options', return_value=[VpsOption(name='Advanced',
                                                                                             storage=2,
                                                                                             cores=2,
                                                                                             memory=2,
                                                                                             bandwidth="mock",
                                                                                             connection="1",
                                                                                             price=100.0,
                                                                                             purchase_url="mock"
                                                                                             ),
                                                                                   VpsOption(name='Basic Plan',
                                                                                             storage=2,
                                                                                             cores=2,
                                                                                             memory=2,
                                                                                             bandwidth="mock",
                                                                                             connection="1",
                                                                                             price=10.0,
                                                                                             purchase_url="mock"
                                                                                             )])
    def test_update_environment_negative(self, mock1, mock2):
        blue_angel_offers = cloudomate_controller.options(self.providers["blueangelhost"])
        self.qtable.self_state = VPSState("blueangelhost", blue_angel_offers[0].name)
        self.qtable.init_qtable_and_environment(self.providers)
        environment_copy = copy.deepcopy(self.qtable.environment)
        vps_options_list = cloudomate_controller.options(self.providers)
        vps_option = vps_options_list[0]

        provider_offer_ID = str(self.providers.keys()[0]).lower() + "_" + str(vps_option.name).lower()
        provider_offer_ID_other = str(self.providers.keys()[0]).lower() + "_" + str(vps_options_list[1].name).lower()

        self.qtable.update_environment(provider_offer_ID, False)
        assert (environment_copy != self.qtable.environment)
        assert (environment_copy[provider_offer_ID][provider_offer_ID] >
                self.qtable.environment[provider_offer_ID][provider_offer_ID])
        assert (environment_copy[provider_offer_ID][provider_offer_ID_other] ==
                self.qtable.environment[provider_offer_ID][provider_offer_ID_other])
        assert(self.qtable.environment[provider_offer_ID][provider_offer_ID] == -0.4)

    @mock.patch('plebnet.controllers.cloudomate_controller.get_vps_providers',
                return_value=CaseInsensitiveDict({'blueangelhost': blueAngel.BlueAngelHost}))
    @mock.patch('plebnet.controllers.cloudomate_controller.options', return_value=[VpsOption(name='Advanced',
                                                                                             storage=2,
                                                                                             cores=2,
                                                                                             memory=2,
                                                                                             bandwidth="mock",
                                                                                             connection="1",
                                                                                             price=100.0,
                                                                                             purchase_url="mock"
                                                                                             ),
                                                                                   VpsOption(name='Basic Plan',
                                                                                             storage=2,
                                                                                             cores=2,
                                                                                             memory=2,
                                                                                             bandwidth="mock",
                                                                                             connection="1",
                                                                                             price=10.0,
                                                                                             purchase_url="mock"
                                                                                             )])
    def test_update_values_positive(self, mock1, mock2):
        blue_angel_offers = cloudomate_controller.options(self.providers["blueangelhost"])
        self.qtable.self_state = VPSState("blueangelhost", blue_angel_offers[0].name)
        self.qtable.init_qtable_and_environment(self.providers)
        qtable_copy = copy.deepcopy(self.qtable.qtable)
        vps_options_list = cloudomate_controller.options(self.providers)
        vps_option = vps_options_list[0]

        provider_offer_ID = str(self.providers.keys()[0]).lower() + "_" + str(vps_option.name).lower()
        provider_offer_ID_other = str(self.providers.keys()[0]).lower() + "_" + str(vps_options_list[1].name).lower()

        self.qtable.update_values(provider_offer_ID, True)
        assert (qtable_copy != self.qtable.qtable)
        assert (qtable_copy[provider_offer_ID_other][provider_offer_ID] <
                self.qtable.qtable[provider_offer_ID_other][provider_offer_ID])
        assert(round(self.qtable.qtable[provider_offer_ID_other][provider_offer_ID],7) == 0.0029975)


    @mock.patch('plebnet.controllers.cloudomate_controller.get_vps_providers',
                return_value=CaseInsensitiveDict({'blueangelhost': blueAngel.BlueAngelHost}))
    @mock.patch('plebnet.controllers.cloudomate_controller.options', return_value=[VpsOption(name='Advanced',
                                                                                             storage=2,
                                                                                             cores=2,
                                                                                             memory=2,
                                                                                             bandwidth="mock",
                                                                                             connection="1",
                                                                                             price=100.0,
                                                                                             purchase_url="mock"
                                                                                             ),
                                                                                   VpsOption(name='Basic Plan',
                                                                                             storage=2,
                                                                                             cores=2,
                                                                                             memory=2,
                                                                                             bandwidth="mock",
                                                                                             connection="1",
                                                                                             price=10.0,
                                                                                             purchase_url="mock"
                                                                                             )])
    def test_update_values_negative(self, mock1, mock2):
        blue_angel_offers = cloudomate_controller.options(self.providers["blueangelhost"])
        self.qtable.self_state = VPSState("blueangelhost", blue_angel_offers[0].name)
        self.qtable.init_qtable_and_environment(self.providers)
        qtable_copy = copy.deepcopy(self.qtable.qtable)
        vps_options_list = cloudomate_controller.options(self.providers)
        vps_option = vps_options_list[0]

        provider_offer_ID = str(self.providers.keys()[0]).lower() + "_" + str(vps_option.name).lower()
        provider_offer_ID_other = str(self.providers.keys()[0]).lower() + "_" + str(vps_options_list[1].name).lower()

        self.qtable.update_values(provider_offer_ID, False)
        assert (qtable_copy != self.qtable.qtable)
        assert (qtable_copy[provider_offer_ID_other][provider_offer_ID] >
                self.qtable.qtable[provider_offer_ID_other][provider_offer_ID])
        assert(round(self.qtable.qtable[provider_offer_ID_other][provider_offer_ID],7) == 0.0009975)


    @mock.patch('plebnet.controllers.cloudomate_controller.get_vps_providers',
                return_value=CaseInsensitiveDict({'blueangelhost': blueAngel.BlueAngelHost}))
    @mock.patch('plebnet.controllers.cloudomate_controller.options', return_value=[VpsOption(name='Advanced',
                                                                                             storage=2,
                                                                                             cores=2,
                                                                                             memory=2,
                                                                                             bandwidth="mock",
                                                                                             connection="1",
                                                                                             price=100.0,
                                                                                             purchase_url="mock"
                                                                                             ),
                                                                                   VpsOption(name='Basic Plan',
                                                                                             storage=2,
                                                                                             cores=2,
                                                                                             memory=2,
                                                                                             bandwidth="mock",
                                                                                             connection="1",
                                                                                             price=10.0,
                                                                                             purchase_url="mock"
                                                                                             )])
    def test_choose_best_option(self, mock1, mock2):
        self.qtable.init_qtable_and_environment(self.providers)
        self.qtable.set_self_state(VPSState("blueangelhost", "Advanced"))
        best_option = self.qtable.choose_best_option(self.providers)

        self.assertEqual(best_option["provider_name"], "blueangelhost")
        self.assertEqual(best_option["option_name"], "Basic Plan")

    @mock.patch('plebnet.controllers.cloudomate_controller.get_vps_providers',
                return_value=CaseInsensitiveDict({'blueangelhost': blueAngel.BlueAngelHost}))
    @mock.patch('plebnet.controllers.cloudomate_controller.options', return_value=[VpsOption(name='Advanced',
                                                                                             storage=2,
                                                                                             cores=2,
                                                                                             memory=2,
                                                                                             bandwidth="mock",
                                                                                             connection="1",
                                                                                             price=100.0,
                                                                                             purchase_url="mock"
                                                                                             ),
                                                                                   VpsOption(name='Basic Plan',
                                                                                             storage=2,
                                                                                             cores=2,
                                                                                             memory=2,
                                                                                             bandwidth="mock",
                                                                                             connection="1",
                                                                                             price=10.0,
                                                                                             purchase_url="mock"
                                                                                             )])
    def test_find_provider(self, mock1, mock2):
        self.qtable.init_qtable_and_environment(self.providers)
        self.qtable.set_self_state(VPSState("blueangelhost", "Advanced"))

        provider_name = self.qtable.find_provider("blueangelhost_basic plan")
        self.assertEqual(provider_name, "blueangelhost")


if __name__ == '__main__':
    unittest.main()
