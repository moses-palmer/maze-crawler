// Return 250 if an exception is uncaught
process.on('uncaughtException', function(e) {
    console.error(e.stack || e);
    process.exit(250);
});

// We use jamine to run the tests
var jasmine = require('jasmine-node');

// Try util, but fall back to sys
var util;
try {
    util = require('util')
}
catch(e) {
    util = require('sys')
}

// Load coffee script
require('coffee-script');

// The following line keeps the jasmine setTimeout in the proper scope
jasmine.setTimeout = jasmine.getGlobal().setTimeout;
jasmine.setInterval = jasmine.getGlobal().setInterval;
for (var key in jasmine) {
    global[key] = jasmine[key];
}

var Reporter = function() {
    this.currentSuite = -1;
    this.results = [];
};
Reporter.prototype = {
    reportRunnerStarting: function(runner) {
        this.currentSuite = -1;
        this.suites = runner.topLevelSuites();
    },

    reportSpecStarting: function(spec) {
        this.log({
            when: 'spec_start',
            spec_id: spec.id,
            description: spec.suite.getFullName() + " " + spec.description});
    },

    reportSpecResults: function(spec) {
        var results = spec.results();

        // Ignore skipped or successful specs
        if (results.skipped || results.passed()) {
            return;
        }

        var failures = [];
        spec.results().getItems().forEach(function(result) {
            // Ignore skipped or passed items
            if (result.skipped || result.passed()) {
                return;
            }

            failures.push({
                message: result.message,
                stacktrace: result.trace.stack});
        });

        this.log({
            when: 'spec_failed',
            spec_id: spec.id,
            failures: failures});
    },

    reportSuiteResults: function(suite) {},

    reportRunnerResults: function(runner) {
        // Do nothing
    },

    log: function(o) {
        var console = jasmine.getGlobal().console;
        if (console && console.log) {
            console.log('\n' + JSON.stringify(o) + '\n');
        }
    }
};

// Add a custom reporter to have full control of the output
jasmine.getEnv().addReporter(new Reporter());

// Set options
jasmine.executeSpecsInFolder({
    specFolders: [process.argv[2]],
    useRequireJs: true,
    regExpSpec: /\.(coffee|js)$/i,
    includeStackTrace: true,

    onComplete: function(runner, log) {
        process.exit(runner.results().failedCount);
    }
});
