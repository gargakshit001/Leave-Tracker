CREATE Table employees (id VARCHAR(50) PRIMARY KEY, name VARCHAR(255) NOT NULL)

SELECT * FROM employees with(noLock)

CREATE Table leaves(
    [id] [INT] IDENTITY(1,1) NOT NULL,
    [employee_id] [VARCHAR](50) NOT NULL,
    [start_date] [DATE] NOT NULL,
    [end_date] [DATE] NOT NULL,
    [type] [VARCHAR](20) NOT NULL,
    FOREIGN KEY (id) REFERENCES employees(id)
)

SELECT * FROM leaves with(noLock)