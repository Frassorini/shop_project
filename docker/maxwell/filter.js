function process_row(row) {
    try {
        // Фильтруем только таблицу task и только INSERT
        if (row.table != "task" || row.type != "insert") {
            row.suppress();
            return;
        }

        if (!row.data) {
            row.suppress();
            return;
        }

        var entity_id = row.data.get("entity_id");
        var handler = row.data.get("handler");

        if (!entity_id || !handler) {
            logger.error("Could not find entity_id or handler in message: " + row.data);
            row.suppress();
            return;
        }

    } catch (e) {
        logger.error("Error processing row: " + e + "\nRow data: " + row.data);
        row.suppress();
    }
}

