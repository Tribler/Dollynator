import copy
import random
import unittest
import unittest.mock as mock
import cloudomate.hoster.vps.blueangelhost as blueAngel
from CaseInsensitiveDict import CaseInsensitiveDict

from cloudomate.hoster.vps.vps_hoster import VpsOption
from unittest.mock import MagicMock

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
        assert (self.qtable.calculate_measure(provider_offer) == 0.024)

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
        assert (self.qtable.calculate_measure(self.qtable.providers_offers[1]) == 0.01)

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
        assert (self.qtable.environment[provider_offer_ID][provider_offer_ID] == 0.4)

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
        assert (self.qtable.environment[provider_offer_ID][provider_offer_ID] == -0.4)

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
        assert (round(self.qtable.qtable[provider_offer_ID_other][provider_offer_ID], 7) == 0.0020125)

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
    def test_update_qtable_from_remote_qtable(self, mock1, mock2):
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
        assert (round(self.qtable.qtable[provider_offer_ID_other][provider_offer_ID], 7) == 0.0020125)

        qtable_copy2 = copy.deepcopy(self.qtable.qtable)

        self.qtable.update_qtable(qtable_copy)

        assert (self.qtable.qtable[provider_offer_ID_other][provider_offer_ID] ==
                (qtable_copy[provider_offer_ID_other][provider_offer_ID] * 0.3 +
                 qtable_copy2[provider_offer_ID_other][provider_offer_ID] * 0.7))

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
        vps_option = vps_options_list[1]

        provider_offer_ID = str(self.providers.keys()[0]).lower() + "_" + str(vps_option.name).lower()
        provider_offer_ID_other = str(self.providers.keys()[0]).lower() + "_" + str(vps_options_list[1].name).lower()

        self.qtable.update_values(provider_offer_ID, False)
        assert (qtable_copy != self.qtable.qtable)
        assert (qtable_copy[provider_offer_ID][provider_offer_ID] >
                self.qtable.qtable[provider_offer_ID][provider_offer_ID])
        assert (round(self.qtable.qtable[provider_offer_ID_other][provider_offer_ID], 7) == 0.0099525)

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
        assert (provider_name == "blueangelhost")

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
    def test_kth_score(self, mock1, mock2):
        self.qtable.init_qtable_and_environment(self.providers)
        self.qtable.set_self_state(VPSState("blueangelhost", "Advanced"))
        assert (self.qtable.get_kth_score(self.providers, 0) == 0.01)

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
    def test_choose_k_option(self, mock1, mock2):
        self.qtable.init_qtable_and_environment(self.providers)
        self.qtable.set_self_state(VPSState("blueangelhost", "Advanced"))
        option = self.qtable.choose_k_option(self.providers, 1)
        assert (option["option_name"] == "Advanced")
        assert (option["price"] == 100.0)

    @mock.patch('plebnet.settings.plebnet_settings.Init.irc_nick', return_value="plebbot1")
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
    def test_choose_option(self, mock1, mock2, mock3):
        self.qtable.init_qtable_and_environment(self.providers)
        self.qtable.set_self_state(VPSState("blueangelhost", "Advanced"))
        random.expovariate = MagicMock(return_value=0.55)
        option = self.qtable.choose_option(self.providers)
        assert (option["option_name"] == "Basic Plan")
        assert (option["price"] == 10.0)

    @mock.patch('plebnet.settings.plebnet_settings.Init.irc_nick', return_value="plebbot1")
    def test_create_initial_tree(self, mock1):
        self.qtable.set_self_state(VPSState("blueangelhost", "Advanced"))
        self.qtable.create_initial_tree()
        assert (self.qtable.tree == "plebbot1")

    def test_get_no_replications(self):
        self.qtable.tree = "plebbot1.2.3"
        self.assertEqual(self.qtable.get_no_replications(), 3)

    def get_ID(self, provider_offer):
        return str(provider_offer.provider_name).lower() + "_" + str(provider_offer.name).lower()

    # @mock.patch('plebnet.controllers.cloudomate_controller.get_vps_providers',
    #             return_value=CaseInsensitiveDict({'blueangelhost': blueAngel.BlueAngelHost}))
    # @mock.patch('plebnet.controllers.cloudomate_controller.options', return_value=[VpsOption(name='Advanced',
    #                                                                                          storage=2,
    #                                                                                          cores=2,
    #                                                                                          memory=2,
    #                                                                                          bandwidth="mock",
    #                                                                                          connection="1",
    #                                                                                          price=100.0,
    #                                                                                          purchase_url="mock"
    #                                                                                          ),
    #                                                                                VpsOption(name='Basic Plan',
    #                                                                                          storage=2,
    #                                                                                          cores=2,
    #                                                                                          memory=2,
    #                                                                                          bandwidth="mock",
    #                                                                                          connection="1",
    #                                                                                          price=10.0,
    #                                                                                          purchase_url="mock"
    #                                                                                          )])
    # def test_update_qtable(self, mock1, mock2):
    #
    #     qtable2 = QTable()
    #
    #     blue_angel_offers = cloudomate_controller.options(self.providers["blueangelhost"])
    #     self.qtable.self_state = VPSState("blueangelhost", blue_angel_offers[0].name)
    #     qtable2.self_state = VPSState("blueangelhost", blue_angel_offers[0].name)
    #
    #     self.qtable.init_qtable_and_environment(self.providers)
    #     qtable2.init_qtable_and_environment(self.providers)
    #
    #     qtable_copy = copy.deepcopy(self.qtable.qtable)
    #     vps_options_list = cloudomate_controller.options(self.providers)
    #     vps_option = vps_options_list[0]
    #
    #     provider_offer_ID = str(self.providers.keys()[0]).lower() + "_" + str(vps_option.name).lower()
    #     provider_offer_ID_other = str(self.providers.keys()[0]).lower() + "_" + str(vps_options_list[1].name).lower()
    #
    #     # state_action = QStateAction(provider_offer_ID, provider_offer_ID)
    #     action = provider_offer_ID
    #     state_action = QStateAction(provider_offer_ID, action)
    #
    #     recieved_qtables = {(qtable2, state_action)}
    #
    #     # self.qtable.update_values(provider_offer_ID, True)
    #     self.qtable.update_recieved_qtables(recieved_qtables, provider_offer_ID, True)
    #
    #     assert (qtable_copy != self.qtable.qtable)
    #     assert (qtable_copy[provider_offer_ID_other][provider_offer_ID] <
    #             self.qtable.qtable[provider_offer_ID_other][provider_offer_ID])
    #     # assert (round(self.qtable.qtable[provider_offer_ID_other][provider_offer_ID], 7) == 0.0020125)


if __name__ == '__main__':
    unittest.main()
