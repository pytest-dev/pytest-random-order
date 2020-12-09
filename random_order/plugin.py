import random
import sys
import traceback
import warnings

import pytest

from random_order.bucket_types import bucket_type_keys, bucket_types
from random_order.cache import process_failed_first_last_failed
from random_order.config import Config
from random_order.shuffler import _disable, _get_set_of_item_ids, _shuffle_items
from collections import OrderedDict 

def pytest_addoption(parser):
    group = parser.getgroup('pytest-random-order options')
    group.addoption(
        '--random-order',
        action='store_true',
        dest='random_order_enabled',
        help='Randomise test order (by default, it is disabled) with default configuration.',
    )
    group.addoption(
        '--random-order-bucket',
        action='store',
        dest='random_order_bucket',
        default=Config.default_value('module'),
        choices=bucket_types,
        help='Randomise test order within specified test buckets.',
    )
    group.addoption(
        '--random-order-seed',
        action='store',
        dest='random_order_seed',
        default=Config.default_value(str(random.randint(1, 1000000))),
        help='Randomise test order using a specific seed.',
    )
    group.addoption(
        '--flaky-test-finder',
        action='store',
        dest='flaky_test_finder',
        default=1,
        help='To find flaky tests by running all the tests specific number of times in random orders.',
    )
    group.addoption(
        '--flaky-test-log-path',
        action='store',
        dest='flaky_test_log_path',
        default="flaky_test.json",
        help='To set the file path for storing the flaky test log file',
    )

def pytest_configure(config):
    config.addinivalue_line(
        'markers',
        'random_order(disabled=True): disable reordering of tests within a module or class'# ,
        # 'flaky-test-finder(n): run the given set of tests in random order `n` times',
        # 'flaky-test-log-path: set the file path for storing the flaky test log file'
    )

def pytest_report_header(config):
    plugin = Config(config)
    if not plugin.is_enabled:
        return "Test order randomisation NOT enabled. Enable with --random-order or --random-order-bucket=<bucket_type>"
    return_string = ""
    if plugin.is_enabled and plugin.flaky_test_finder <= 1:
        return_string = return_string + "Flaky test finder NOT enabled. Enable with --flaky-test-finder=<repition_number> where repition_number>1\n"
    if plugin.flaky_test_log_path:
        return_string = return_string + "Flaky test log path NOT enabled. Enable with --flaky-test-log-path=<log_path>\n"
    return return_string + (
        'Using --random-order-bucket={plugin.bucket_type}\n'
        'Using --random-order-seed={plugin.seed}\n'
    ).format(plugin=plugin)

def pytest_collection_modifyitems(session, config, items):
    failure = None

    session.random_order_bucket_type_key_handlers = []
    process_failed_first_last_failed(session, config, items)

    item_ids = _get_set_of_item_ids(items)

    plugin = Config(config)

    try:
        seed = plugin.seed
        bucket_type = plugin.bucket_type
        if bucket_type != 'none':
            _shuffle_items(
                items,
                bucket_key=bucket_type_keys[bucket_type],
                disable=_disable,
                seed=seed,
                session=session,
            )
        
        # print("Shuffle Doneeeee")
        # print("\nItems:", items)
        
        if plugin.flaky_test_finder>1:
            new_items = reorder_based_on_the_test_set(items)
            # Deep Copy is required
            for idx, item in enumerate(new_items):
                items[idx] = item
            # print("\nReordering done based on test_set")

        # print("\nItems:", items)
        
    except Exception as e:
        # See the finally block -- we only fail if we have lost user's tests.
        _, _, exc_tb = sys.exc_info()
        failure = 'pytest-random-order plugin has failed with {0!r}:\n{1}'.format(
            e, ''.join(traceback.format_tb(exc_tb, 10))
        )
        if not hasattr(pytest, "PytestWarning"):
            config.warn(0, failure, None)
        else:
            warnings.warn(pytest.PytestWarning(failure))

    finally:
        # Fail only if we have lost user's tests
        if item_ids != _get_set_of_item_ids(items):
            if not failure:
                failure = 'pytest-random-order plugin has failed miserably'
            raise RuntimeError(failure)

@pytest.hookimpl(trylast=True)
def pytest_generate_tests(metafunc):
    plugin = Config(metafunc.config)
    if plugin.flaky_test_finder > 1:
        metafunc.fixturenames.append("_pytest_random_order_repeat_number")
        def add_repeat_id(i, n=plugin.flaky_test_finder):
            return 'flaky-repeat_{0}-{1}'.format(i + 1, n)
        metafunc.parametrize('_pytest_random_order_repeat_number', range(plugin.flaky_test_finder), indirect=True, ids=add_repeat_id, scope="module")

set_of_flaky_tests = set() # Set of Flaky Tests
tests_order_logger = OrderedDict() # Stores the test order
test_and_outcome_for_output_file = OrderedDict() # Stores the "original_test_name" = { "run_<number>" = { "order" = [], "outcome" = ""} }; run_<number> is 0-indexed

def pytest_report_teststatus(report, config):
    try:
        plugin = Config(config)
        if report.when == 'call' and plugin.flaky_test_finder>1:
            prefix = 'flaky-repeat_'
            suffix = ']'
            original_test_name = report.nodeid.split('[')[0]
            # print("\noriginal_test_name: ",original_test_name)
            # print("\nreport.nodeid: ",report.nodeid)
            repeat_number = int(report.nodeid[report.nodeid.find(prefix)+len(prefix) : report.nodeid.find(suffix)][0]) - 1

            # Check if current test is flaky or not
            if repeat_number>0 and original_test_name in tests_order_logger:
                if report.outcome != tests_order_logger[original_test_name]:
                    set_of_flaky_tests.add(original_test_name)

            # Update tests_order_logger
            if original_test_name in tests_order_logger:
                tests_order_logger.pop(original_test_name)
            tests_order_logger[original_test_name] = report.outcome

            # Update test_and_outcome_for_output_file
            test_and_outcome_for_output_file[original_test_name]["run_"+str(repeat_number)]["outcome"] = report.outcome
            test_and_outcome_for_output_file[original_test_name]["run_"+str(repeat_number)]["order"] = list(tests_order_logger.keys())
    except:
        print('Unexpected error raised by pytest-random-order plugin: {}. {}, line: {}'.format(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2].tb_lineno))

def pytest_terminal_summary(terminalreporter, exitstatus, config):
    plugin = Config(config)
    if plugin.flaky_test_finder>1:
        if len(set_of_flaky_tests):
            print("\nList of Flaky Tests: ", set_of_flaky_tests)
        else:
            print("\nList of Flaky Tests: None")
        
        #Extract flaky test ordering log data
        flaky_test_log_data = {}
        for flaky_test in set_of_flaky_tests:
            if flaky_test in test_and_outcome_for_output_file:
                flaky_test_log_data[flaky_test] = test_and_outcome_for_output_file[flaky_test]
        # add additional fields to the logged dictionary: "list_of_tests_ran", "random_order_seed", "random_order_bucket", flaky_test_repeat_count"
        flaky_test_log_data["list_of_tests_ran"] = list(tests_order_logger.keys())
        flaky_test_log_data["random_order_seed"] = plugin.seed
        flaky_test_log_data["random_order_bucket"] = plugin.bucket_type
        flaky_test_log_data["flaky_test_finder"] = plugin.flaky_test_finder

        #Export the flaky test log data to file
        import json
        plugin = Config(config)
        try:
            with open(plugin.flaky_test_log_path,"w+") as f:
                json.dump(flaky_test_log_data,f)
        except IOError as e:
            print("I/O error({0}): {1}".format(e.errno, e.strerror))
        except: #handle other exceptions such as attribute errors
            print('Unexpected error raised by pytest-random-order plugin: {}. {}, line: {}'.format(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2].tb_lineno))

def reorder_based_on_the_test_set(items):
    # Sanity Check
    if items is None or len(items)==0:
        return items

    # Get the ids of the item: If repeat was set to 2 then test id would be: fileName.py::testName[1-2] where 1 is repeat number and 2 is number of total repeats
    # print("\nList of Item IDs:", list(item.nodeid for item in items))
    
    try:
        # Sort in place based on number of times asked to repeat
        list_of_repeat = []
        prefix = 'flaky-repeat_'
        suffix = ']'
        number_of_repeat = int(items[0].nodeid[items[0].nodeid.find(prefix)+len(prefix): items[0].nodeid.find(suffix)][2])
        for i in range(number_of_repeat):
            list_of_repeat.append([])
        for item in items:
            # Extract Repeat Number and Number of Repeats
            repeat_number = int(item.nodeid[item.nodeid.find(prefix)+len(prefix) : item.nodeid.find(suffix)][0]) - 1
            # Add it to the corresponding repeat bucket
            list_of_repeat[repeat_number].append(item)

            # Initialise test_and_outcome_for_output_file
            original_test_name = item.nodeid.split('[')[0]
            if original_test_name not in test_and_outcome_for_output_file:
                test_and_outcome_for_output_file[original_test_name] = OrderedDict()
                for i in range(number_of_repeat):
                    test_and_outcome_for_output_file[original_test_name]["run_"+str(i)] = {}
        new_items = []
        for repeat_bucket in list_of_repeat:
            new_items += repeat_bucket
        return new_items
    except:
        print('Unexpected error raised by pytest-random-order plugin: {}. {}, line: {}'.format(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2].tb_lineno))