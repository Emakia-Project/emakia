// config.js

module.exports = {
    bq: {
        defaultDataSetName: 'dataset_lucile', // Default dataset name
        table: {
            tweets: 'tweets_table', // Default tweets table name
            users: 'users_table', // Default users table name
            media: 'media_table' // Default media table name
        }
        // Other BigQuery configurations if needed
    },
    // Other configurations for your application
};

