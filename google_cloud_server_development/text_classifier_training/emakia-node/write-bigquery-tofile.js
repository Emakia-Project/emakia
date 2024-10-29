const { BigQuery } = require('@google-cloud/bigquery');

async function getTableSchema() {
  const bigquery = new BigQuery();
  const query = `
    SELECT 
      column_name,
      FROM \`webhemakia.Harassment.INFORMATION_SCHEMA.COLUMNS\`
      WHERE table_name = 'tweets';
  `;

  try {
    const [rows] = await bigquery.query(query);
    rows.forEach(row => {
      // Output basic column information
      console.log(`Column: ${row.column_name}`);

      // If the column is nested, handle it accordingly
      // For example, if the column name contains '.', it's nested
      if (row.column_name.includes('.')) {
        console.log('nestedcolumns');
        const nestedColumns = row.column_name.split('.');
        console.log('Nested Columns:', nestedColumns);
        // You can further process the nested columns here if needed
      }
    });
  } catch (err) {
    console.error('Error fetching schema:', err);
  }
}

getTableSchema();
