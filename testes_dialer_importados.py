"""
Testes importados do Dialer Example.csv
Gerado automaticamente por importar_testes_dialer.py
"""

from src.models.test_case import TestCase, Action, ActionType, ActionImpact


def criar_testes_dialer():
    """Retorna lista de testes do módulo Dialer importados do CSV."""
    return [
        TestCase(
            id="TEST-0001",
            name='Open Keypad on dialer',
            description='Open Keypad on dialer\n\nResultado Esperado: 1- The app shall be open without errors\n2- The keypad is open and is possible to see the numbers 0-9 and a green button “Call”',
            priority=3,
            module='Telephony',
            tags={'dialer', 'imported', 'csv'},
            dependencies=set(),
            validation_point_action='TEST-0001_A002',
            actions=[
                Action(
                    id='TEST-0001_A001',
                    description='Open dialer app',
                    action_type=ActionType.NAVIGATION,
                    impact=ActionImpact.PARTIALLY_DESTRUCTIVE,
                    preconditions=set(),
                    postconditions={'dialer_open'},
                    estimated_time=3.0,
                    priority=1,
                    tags={'dialer', 'imported'}
                ),
                Action(
                    id='TEST-0001_A002',
                    description='Open Keypad',
                    action_type=ActionType.NAVIGATION,
                    impact=ActionImpact.PARTIALLY_DESTRUCTIVE,
                    preconditions={'dialer_open'},
                    postconditions={'keypad_open'},
                    estimated_time=3.0,
                    priority=1,
                    tags={'dialer', 'imported'}
                ),
            ]
        ),
        TestCase(
            id="TEST-0002",
            name='Check INFO hidden menu',
            description='Check INFO hidden menu\n\nResultado Esperado: 1- The keypad is displayed\n2- The hidden menu of phone info is displayed containing the options phone usage and phone info',
            priority=2,
            module='System Settings',
            tags={'dialer', 'imported', 'csv'},
            dependencies=set(),
            validation_point_action='TEST-0002_A001',
            context_preserving=True,
            actions=[
                Action(
                    id='TEST-0002_A001',
                    description='Go to Keypad on Dialer app',
                    action_type=ActionType.NAVIGATION,
                    impact=ActionImpact.PARTIALLY_DESTRUCTIVE,
                    preconditions={'dialer_open'},
                    postconditions={'step_1_completed'},
                    estimated_time=3.0,
                    priority=1,
                    tags={'dialer', 'imported'}
                ),
                Action(
                    id='TEST-0002_A002',
                    description='type *#*#INFO#*#*',
                    action_type=ActionType.CREATION,
                    impact=ActionImpact.PARTIALLY_DESTRUCTIVE,
                    preconditions={'keypad_open'},
                    postconditions={'step_2_executed'},
                    estimated_time=5.0,
                    priority=1,
                    tags={'dialer', 'imported'}
                ),
            ]
        ),
        TestCase(
            id="TEST-0003",
            name='Check phone info menu',
            description='Check phone info menu\n\nResultado Esperado: 1- The keypad is displayed\n2- The hidden menu of phone info is displayed containing the options phone usage and phone info',
            priority=2,
            module='System Settings',
            tags={'dialer', 'imported', 'csv'},
            dependencies=set(),
            validation_point_action='TEST-0003_A001',
            context_preserving=True,
            actions=[
                Action(
                    id='TEST-0003_A001',
                    description='Go Dialer > Keypad',
                    action_type=ActionType.NAVIGATION,
                    impact=ActionImpact.NON_DESTRUCTIVE,
                    preconditions={'dialer_open'},
                    postconditions={'step_1_completed'},
                    estimated_time=3.0,
                    priority=1,
                    tags={'dialer', 'imported'}
                ),
                Action(
                    id='TEST-0003_A002',
                    description='Type *#*#INFO#*#*',
                    action_type=ActionType.CREATION,
                    impact=ActionImpact.PARTIALLY_DESTRUCTIVE,
                    preconditions={'keypad_open'},
                    postconditions={'step_2_executed'},
                    estimated_time=5.0,
                    priority=1,
                    tags={'dialer', 'imported'}
                ),
                Action(
                    id='TEST-0003_A003',
                    description='Check phone info menu',
                    action_type=ActionType.VERIFICATION,
                    impact=ActionImpact.NON_DESTRUCTIVE,
                    preconditions={'hidden_menu_displayed'},
                    postconditions={'phone_info_menu_displayed', 'hidden_menu_displayed'},
                    estimated_time=2.0,
                    priority=1,
                    tags={'dialer', 'imported'}
                ),
            ]
        ),
        TestCase(
            id="TEST-0004",
            name='Check phone usage menu',
            description='Check phone usage menu\n\nResultado Esperado: 1- The keypad is displayed\n2- The hidden menu of testing is displayed with the option of phone info\n3- A list of apps with the usage time and last used hour is displayed',
            priority=2,
            module='Telephony',
            tags={'dialer', 'imported', 'csv'},
            dependencies=set(),
            validation_point_action='TEST-0004_A001',
            teardown_restores=True,
            actions=[
                Action(
                    id='TEST-0004_A001',
                    description='Go Dialer > Keypad',
                    action_type=ActionType.NAVIGATION,
                    impact=ActionImpact.NON_DESTRUCTIVE,
                    preconditions={'dialer_open'},
                    postconditions={'step_1_completed'},
                    estimated_time=3.0,
                    priority=1,
                    tags={'dialer', 'imported'}
                ),
                Action(
                    id='TEST-0004_A002',
                    description='Type *#*#INFO#*#*',
                    action_type=ActionType.CREATION,
                    impact=ActionImpact.PARTIALLY_DESTRUCTIVE,
                    preconditions={'keypad_open'},
                    postconditions={'step_2_executed'},
                    estimated_time=5.0,
                    priority=1,
                    tags={'dialer', 'imported'}
                ),
                Action(
                    id='TEST-0004_A003',
                    description='Check phone usage',
                    action_type=ActionType.VERIFICATION,
                    impact=ActionImpact.NON_DESTRUCTIVE,
                    preconditions={'hidden_menu_displayed'},
                    postconditions={'phone_usage_displayed'},
                    estimated_time=2.0,
                    priority=1,
                    tags={'dialer', 'imported'}
                ),
            ]
        ),
        TestCase(
            id="TEST-0005",
            name='Set prefered network on hidden menu',
            description='Set prefered network on hidden menu\n\nResultado Esperado: 1- The keypad is displayed\n2- The hidden menu of testing is displayed with the option of phone info\n3- The phone info is displayed\n4- The phone shall change its network, sucessfuly when the network is available\n\nPré-requisitos: Device shall have a valid SIM card',
            priority=5,
            module='System Settings',
            tags={'dialer', 'imported', 'csv'},
            dependencies=set(),
            validation_point_action='TEST-0005_A001',
            actions=[
                Action(
                    id='TEST-0005_A001',
                    description='Go Dialer > Keypad',
                    action_type=ActionType.NAVIGATION,
                    impact=ActionImpact.NON_DESTRUCTIVE,
                    preconditions={'device_configured', 'sim_card_inserted', 'dialer_open'},
                    postconditions={'step_1_completed'},
                    estimated_time=3.0,
                    priority=1,
                    tags={'dialer', 'imported'}
                ),
                Action(
                    id='TEST-0005_A002',
                    description='Type *#*#INFO#*#*',
                    action_type=ActionType.CREATION,
                    impact=ActionImpact.PARTIALLY_DESTRUCTIVE,
                    preconditions={'device_configured', 'keypad_open', 'sim_card_inserted'},
                    postconditions={'step_2_executed'},
                    estimated_time=5.0,
                    priority=1,
                    tags={'dialer', 'imported'}
                ),
                Action(
                    id='TEST-0005_A003',
                    description='Open phone info menu',
                    action_type=ActionType.NAVIGATION,
                    impact=ActionImpact.PARTIALLY_DESTRUCTIVE,
                    preconditions={'device_configured', 'hidden_menu_displayed', 'sim_card_inserted'},
                    postconditions={'phone_info_menu_displayed', 'hidden_menu_displayed'},
                    estimated_time=3.0,
                    priority=1,
                    tags={'dialer', 'imported'}
                ),
                Action(
                    id='TEST-0005_A004',
                    description='Set prefered network to 5G/4G/3G',
                    action_type=ActionType.CREATION,
                    impact=ActionImpact.PARTIALLY_DESTRUCTIVE,
                    preconditions={'device_configured', 'sim_card_inserted'},
                    postconditions={'network_preference_set'},
                    estimated_time=5.0,
                    priority=1,
                    tags={'dialer', 'imported'}
                ),
            ]
        ),
        TestCase(
            id="TEST-0006",
            name='Check options in keypad when number is not on contacts',
            description='Check options in keypad when number is not on contacts\n\nResultado Esperado: 1- The dialer app is displayed\n2- The keypad with the number buttons are displayed\n3- The phone shall display the following options: “Create contact”, “Add to a contact” and “send a message”',
            priority=2,
            module='Telephony',
            tags={'dialer', 'imported', 'csv'},
            dependencies=set(),
            validation_point_action='TEST-0006_A001',
            actions=[
                Action(
                    id='TEST-0006_A001',
                    description='Open dialer app',
                    action_type=ActionType.NAVIGATION,
                    impact=ActionImpact.PARTIALLY_DESTRUCTIVE,
                    preconditions=set(),
                    postconditions={'dialer_open'},
                    estimated_time=3.0,
                    priority=1,
                    tags={'dialer', 'imported'}
                ),
                Action(
                    id='TEST-0006_A002',
                    description='Open Keypad',
                    action_type=ActionType.NAVIGATION,
                    impact=ActionImpact.PARTIALLY_DESTRUCTIVE,
                    preconditions={'dialer_open'},
                    postconditions={'keypad_open'},
                    estimated_time=3.0,
                    priority=1,
                    tags={'dialer', 'imported'}
                ),
                Action(
                    id='TEST-0006_A003',
                    description='Type a number not in contacts',
                    action_type=ActionType.CREATION,
                    impact=ActionImpact.PARTIALLY_DESTRUCTIVE,
                    preconditions={'keypad_open'},
                    postconditions={'number_entered'},
                    estimated_time=5.0,
                    priority=1,
                    tags={'dialer', 'imported'}
                ),
            ]
        ),
        TestCase(
            id="TEST-0007",
            name='Start voice call and upgrade to video',
            description='Start voice call and upgrade to video\n\nResultado Esperado: 1- The dialer app is displayed\n2- The keypad with the number buttons are displayed\n3- The phone shall display the following options: “Create contact”, “Add to a contact” and “send a message”\n\nPré-requisitos: DUT and SUP available\nBoth devices have a valid SIM card',
            priority=3,
            module='Video Calls',
            tags={'dialer', 'imported', 'csv'},
            dependencies=set(),
            validation_point_action='TEST-0007_A001',
            actions=[
                Action(
                    id='TEST-0007_A001',
                    description='Open dialer app',
                    action_type=ActionType.NAVIGATION,
                    impact=ActionImpact.PARTIALLY_DESTRUCTIVE,
                    preconditions={'device_configured', 'dut_and_sup_available', 'sim_card_inserted'},
                    postconditions={'dialer_open'},
                    estimated_time=3.0,
                    priority=1,
                    tags={'dialer', 'imported'}
                ),
                Action(
                    id='TEST-0007_A002',
                    description='Open Keypad',
                    action_type=ActionType.NAVIGATION,
                    impact=ActionImpact.PARTIALLY_DESTRUCTIVE,
                    preconditions={'device_configured', 'dut_and_sup_available', 'sim_card_inserted', 'dialer_open'},
                    postconditions={'keypad_open'},
                    estimated_time=3.0,
                    priority=1,
                    tags={'dialer', 'imported'}
                ),
                Action(
                    id='TEST-0007_A003',
                    description='Type a number of a support device',
                    action_type=ActionType.CREATION,
                    impact=ActionImpact.PARTIALLY_DESTRUCTIVE,
                    preconditions={'device_configured', 'keypad_open', 'dut_and_sup_available', 'sim_card_inserted'},
                    postconditions={'number_entered'},
                    estimated_time=5.0,
                    priority=1,
                    tags={'dialer', 'imported'}
                ),
                Action(
                    id='TEST-0007_A004',
                    description='Start a voice call',
                    action_type=ActionType.NAVIGATION,
                    impact=ActionImpact.PARTIALLY_DESTRUCTIVE,
                    preconditions={'device_configured', 'keypad_open', 'dut_and_sup_available', 'sim_card_inserted'},
                    postconditions={'voice_call_active'},
                    estimated_time=13.0,
                    priority=1,
                    tags={'dialer', 'imported'}
                ),
                Action(
                    id='TEST-0007_A005',
                    description='Upgrade call to a video call',
                    action_type=ActionType.MODIFICATION,
                    impact=ActionImpact.DESTRUCTIVE,
                    preconditions={'device_configured', 'voice_call_active', 'dut_and_sup_available', 'sim_card_inserted'},
                    postconditions={'call_upgraded_to_video'},
                    estimated_time=18.0,
                    priority=1,
                    tags={'dialer', 'imported'}
                ),
            ]
        ),
        TestCase(
            id="TEST-0008",
            name='Start voice call and create conference',
            description='Start voice call and create conference\n\nResultado Esperado: 4- The voice call started and the SUP receives an incoming call\n5- The call is stablished\n6- The display change to conference layout and the incoming call is visible on the SUP2\n\nPré-requisitos: DUT, SUP and SUP2 available\nAll devices have a valid SIM card',
            priority=3,
            module='Conference Calls',
            tags={'dialer', 'imported', 'csv'},
            dependencies=set(),
            validation_point_action='TEST-0008_A001',
            actions=[
                Action(
                    id='TEST-0008_A001',
                    description='Open dialer app',
                    action_type=ActionType.NAVIGATION,
                    impact=ActionImpact.PARTIALLY_DESTRUCTIVE,
                    preconditions={'sim_card_inserted', 'device_configured', 'sup2_available', 'dut_and_sup_available'},
                    postconditions={'dialer_open'},
                    estimated_time=3.0,
                    priority=1,
                    tags={'dialer', 'imported'}
                ),
                Action(
                    id='TEST-0008_A002',
                    description='Open Keypad',
                    action_type=ActionType.NAVIGATION,
                    impact=ActionImpact.PARTIALLY_DESTRUCTIVE,
                    preconditions={'sim_card_inserted', 'device_configured', 'sup2_available', 'dut_and_sup_available', 'dialer_open'},
                    postconditions={'keypad_open'},
                    estimated_time=3.0,
                    priority=1,
                    tags={'dialer', 'imported'}
                ),
                Action(
                    id='TEST-0008_A003',
                    description='Type a number of a SUP',
                    action_type=ActionType.CREATION,
                    impact=ActionImpact.PARTIALLY_DESTRUCTIVE,
                    preconditions={'device_configured', 'keypad_open', 'sup2_available', 'dut_and_sup_available', 'sim_card_inserted'},
                    postconditions={'number_entered'},
                    estimated_time=5.0,
                    priority=1,
                    tags={'dialer', 'imported'}
                ),
                Action(
                    id='TEST-0008_A004',
                    description='Start call',
                    action_type=ActionType.NAVIGATION,
                    impact=ActionImpact.PARTIALLY_DESTRUCTIVE,
                    preconditions={'device_configured', 'dut_and_sup_available', 'sim_card_inserted', 'sup2_available'},
                    postconditions={'step_4_completed'},
                    estimated_time=13.0,
                    priority=1,
                    tags={'dialer', 'imported'}
                ),
                Action(
                    id='TEST-0008_A005',
                    description='Answer the call in the SUP',
                    action_type=ActionType.NAVIGATION,
                    impact=ActionImpact.NON_DESTRUCTIVE,
                    preconditions={'device_configured', 'dut_and_sup_available', 'sim_card_inserted', 'sup2_available'},
                    postconditions={'call_answered'},
                    estimated_time=18.0,
                    priority=1,
                    tags={'dialer', 'imported'}
                ),
                Action(
                    id='TEST-0008_A006',
                    description='Select the conference phone and start a conference call with a SUP2',
                    action_type=ActionType.NAVIGATION,
                    impact=ActionImpact.PARTIALLY_DESTRUCTIVE,
                    preconditions={'device_configured', 'sup2_available', 'call_active', 'dut_and_sup_available', 'sim_card_inserted'},
                    postconditions={'conference_active'},
                    estimated_time=13.0,
                    priority=1,
                    tags={'dialer', 'imported'}
                ),
            ]
        ),
        TestCase(
            id="TEST-0009",
            name='Downgrade video call to voice only',
            description='Downgrade video call to voice only\n\nResultado Esperado: 1- The keypad is displayed\n2- The SUP number is displayed and the buttons to start a voice call, video call and send message are displayed\n3- The video call is stablished without errors\n4- The layout changes to a voice call the video is not available anymore\n\nPré-requisitos: DUT and SUP available\nBoth devices have a valid SIM card',
            priority=3,
            module='Video Calls',
            tags={'dialer', 'imported', 'csv'},
            dependencies=set(),
            validation_point_action='TEST-0009_A004',
            actions=[
                Action(
                    id='TEST-0009_A001',
                    description='Go Dialer > Keypad',
                    action_type=ActionType.NAVIGATION,
                    impact=ActionImpact.NON_DESTRUCTIVE,
                    preconditions={'device_configured', 'dut_and_sup_available', 'sim_card_inserted', 'dialer_open'},
                    postconditions={'step_1_completed'},
                    estimated_time=3.0,
                    priority=1,
                    tags={'dialer', 'imported'}
                ),
                Action(
                    id='TEST-0009_A002',
                    description='Type a number of a SUP',
                    action_type=ActionType.CREATION,
                    impact=ActionImpact.PARTIALLY_DESTRUCTIVE,
                    preconditions={'device_configured', 'keypad_open', 'dut_and_sup_available', 'sim_card_inserted'},
                    postconditions={'number_entered'},
                    estimated_time=5.0,
                    priority=1,
                    tags={'dialer', 'imported'}
                ),
                Action(
                    id='TEST-0009_A003',
                    description='Start a video call with SUP',
                    action_type=ActionType.NAVIGATION,
                    impact=ActionImpact.PARTIALLY_DESTRUCTIVE,
                    preconditions={'device_configured', 'keypad_open', 'dut_and_sup_available', 'sim_card_inserted'},
                    postconditions={'video_call_active'},
                    estimated_time=13.0,
                    priority=1,
                    tags={'dialer', 'imported'}
                ),
                Action(
                    id='TEST-0009_A004',
                    description='Downgrade to voice only',
                    action_type=ActionType.MODIFICATION,
                    impact=ActionImpact.DESTRUCTIVE,
                    preconditions={'device_configured', 'video_call_active', 'dut_and_sup_available', 'sim_card_inserted'},
                    postconditions={'call_downgraded_to_voice'},
                    estimated_time=8.0,
                    priority=1,
                    tags={'dialer', 'imported'}
                ),
            ]
        ),
        TestCase(
            id="TEST-0010",
            name='Answer incoming video call as voice only',
            description='Answer incoming video call as voice only\n\nResultado Esperado: 1- The dialer is displayed\n2- The keypad is displayed\n3- The video call is started without errors and the SUP receives the incoming video call\n4- The call is stablished as a voice call, no video is displayed in both devices\n\nPré-requisitos: DUT and SUP available\nBoth devices have a valid SIM card',
            priority=3,
            module='Video Calls',
            tags={'dialer', 'imported', 'csv'},
            dependencies=set(),
            validation_point_action='TEST-0010_A001',
            actions=[
                Action(
                    id='TEST-0010_A001',
                    description='Open dialer app',
                    action_type=ActionType.NAVIGATION,
                    impact=ActionImpact.PARTIALLY_DESTRUCTIVE,
                    preconditions={'device_configured', 'dut_and_sup_available', 'sim_card_inserted'},
                    postconditions={'dialer_open'},
                    estimated_time=3.0,
                    priority=1,
                    tags={'dialer', 'imported'}
                ),
                Action(
                    id='TEST-0010_A002',
                    description='Open Keypad',
                    action_type=ActionType.NAVIGATION,
                    impact=ActionImpact.PARTIALLY_DESTRUCTIVE,
                    preconditions={'device_configured', 'dut_and_sup_available', 'sim_card_inserted', 'dialer_open'},
                    postconditions={'keypad_open'},
                    estimated_time=3.0,
                    priority=1,
                    tags={'dialer', 'imported'}
                ),
                Action(
                    id='TEST-0010_A003',
                    description='Start a video call with a support device',
                    action_type=ActionType.NAVIGATION,
                    impact=ActionImpact.PARTIALLY_DESTRUCTIVE,
                    preconditions={'device_configured', 'keypad_open', 'dut_and_sup_available', 'sim_card_inserted'},
                    postconditions={'video_call_active'},
                    estimated_time=13.0,
                    priority=1,
                    tags={'dialer', 'imported'}
                ),
                Action(
                    id='TEST-0010_A004',
                    description='Answer the call in the SUP as voice only',
                    action_type=ActionType.NAVIGATION,
                    impact=ActionImpact.NON_DESTRUCTIVE,
                    preconditions={'device_configured', 'dut_and_sup_available', 'sim_card_inserted'},
                    postconditions={'call_answered'},
                    estimated_time=18.0,
                    priority=1,
                    tags={'dialer', 'imported'}
                ),
            ]
        ),
        TestCase(
            id="TEST-0011",
            name='Start Video call',
            description='Start Video call\n\nResultado Esperado: 1- The dialer is displayed\n2- The keypad is displayed\n3- The video call is started and SUP receives an incoming video call\n4- The video call is stablished and both devices can see each other videos\n\nPré-requisitos: DUT and SUP available\nBoth devices have a valid SIM card',
            priority=3,
            module='Video Calls',
            tags={'dialer', 'imported', 'csv'},
            dependencies=set(),
            validation_point_action='TEST-0011_A001',
            actions=[
                Action(
                    id='TEST-0011_A001',
                    description='Open dialer app',
                    action_type=ActionType.NAVIGATION,
                    impact=ActionImpact.PARTIALLY_DESTRUCTIVE,
                    preconditions={'device_configured', 'dut_and_sup_available', 'sim_card_inserted'},
                    postconditions={'dialer_open'},
                    estimated_time=3.0,
                    priority=1,
                    tags={'dialer', 'imported'}
                ),
                Action(
                    id='TEST-0011_A002',
                    description='Open Keypad',
                    action_type=ActionType.NAVIGATION,
                    impact=ActionImpact.PARTIALLY_DESTRUCTIVE,
                    preconditions={'device_configured', 'dut_and_sup_available', 'sim_card_inserted', 'dialer_open'},
                    postconditions={'keypad_open'},
                    estimated_time=3.0,
                    priority=1,
                    tags={'dialer', 'imported'}
                ),
                Action(
                    id='TEST-0011_A003',
                    description='Start a video call with a support device',
                    action_type=ActionType.NAVIGATION,
                    impact=ActionImpact.PARTIALLY_DESTRUCTIVE,
                    preconditions={'device_configured', 'keypad_open', 'dut_and_sup_available', 'sim_card_inserted'},
                    postconditions={'video_call_active'},
                    estimated_time=13.0,
                    priority=1,
                    tags={'dialer', 'imported'}
                ),
                Action(
                    id='TEST-0011_A004',
                    description='Answer the video call in the SUP',
                    action_type=ActionType.NAVIGATION,
                    impact=ActionImpact.NON_DESTRUCTIVE,
                    preconditions={'device_configured', 'incoming_call', 'dut_and_sup_available', 'sim_card_inserted'},
                    postconditions={'call_answered'},
                    estimated_time=18.0,
                    priority=1,
                    tags={'dialer', 'imported'}
                ),
            ]
        ),
        TestCase(
            id="TEST-0012",
            name='Start Video call and expand to a video conference',
            description='Start Video call and expand to a video conference\n\nResultado Esperado: 1- The dialer is displayed\n2- The keypad is displayed\n3- The video call is started and SUP receives an incoming call\n4- The video call is stablished\n5- A conference video call is stablished between DUT, SUP and SUP2\n6- The conference is downgraded and not is a voice only conference, the devices stay in the same call.\n\nPré-requisitos: DUT, SUP and SUP2 available\nAll devices have a valid SIM card',
            priority=3,
            module='Video Calls',
            tags={'dialer', 'imported', 'csv'},
            dependencies=set(),
            validation_point_action='TEST-0012_A001',
            actions=[
                Action(
                    id='TEST-0012_A001',
                    description='Open dialer app',
                    action_type=ActionType.NAVIGATION,
                    impact=ActionImpact.PARTIALLY_DESTRUCTIVE,
                    preconditions={'sim_card_inserted', 'device_configured', 'sup2_available', 'dut_and_sup_available'},
                    postconditions={'dialer_open'},
                    estimated_time=3.0,
                    priority=1,
                    tags={'dialer', 'imported'}
                ),
                Action(
                    id='TEST-0012_A002',
                    description='Open Keypad',
                    action_type=ActionType.NAVIGATION,
                    impact=ActionImpact.PARTIALLY_DESTRUCTIVE,
                    preconditions={'sim_card_inserted', 'device_configured', 'sup2_available', 'dut_and_sup_available', 'dialer_open'},
                    postconditions={'keypad_open'},
                    estimated_time=3.0,
                    priority=1,
                    tags={'dialer', 'imported'}
                ),
                Action(
                    id='TEST-0012_A003',
                    description='Start a video call with a SUP',
                    action_type=ActionType.NAVIGATION,
                    impact=ActionImpact.PARTIALLY_DESTRUCTIVE,
                    preconditions={'device_configured', 'keypad_open', 'sup2_available', 'dut_and_sup_available', 'sim_card_inserted'},
                    postconditions={'video_call_active'},
                    estimated_time=13.0,
                    priority=1,
                    tags={'dialer', 'imported'}
                ),
                Action(
                    id='TEST-0012_A004',
                    description='Answer the video call in the SUP',
                    action_type=ActionType.NAVIGATION,
                    impact=ActionImpact.NON_DESTRUCTIVE,
                    preconditions={'device_configured', 'incoming_call', 'sup2_available', 'dut_and_sup_available', 'sim_card_inserted'},
                    postconditions={'call_answered'},
                    estimated_time=18.0,
                    priority=1,
                    tags={'dialer', 'imported'}
                ),
                Action(
                    id='TEST-0012_A005',
                    description='Add a SUP2 to create a conference',
                    action_type=ActionType.NAVIGATION,
                    impact=ActionImpact.NON_DESTRUCTIVE,
                    preconditions={'device_configured', 'sup2_available', 'call_active', 'dut_and_sup_available', 'sim_card_inserted'},
                    postconditions={'conference_active'},
                    estimated_time=13.0,
                    priority=1,
                    tags={'dialer', 'imported'}
                ),
                Action(
                    id='TEST-0012_A006',
                    description='Downgrade the call to a voice only',
                    action_type=ActionType.MODIFICATION,
                    impact=ActionImpact.DESTRUCTIVE,
                    preconditions={'device_configured', 'video_call_active', 'sup2_available', 'dut_and_sup_available', 'sim_card_inserted'},
                    postconditions={'call_downgraded_to_voice'},
                    estimated_time=18.0,
                    priority=1,
                    tags={'dialer', 'imported'}
                ),
            ]
        ),
    ]
