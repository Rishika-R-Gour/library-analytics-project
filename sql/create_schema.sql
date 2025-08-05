-- 📊 Enhanced Library Management Schema
-- Complete database schema for advanced analytics

-- Core library management tables
CREATE TABLE IF NOT EXISTS Member (
    Member_ID INTEGER PRIMARY KEY,
    Name TEXT,
    Email TEXT,
    Phone TEXT,
    Member_Type TEXT
);

CREATE TABLE IF NOT EXISTS Library (
    Library_ID INTEGER PRIMARY KEY,
    Library_Name TEXT,
    Address TEXT,
    Phone TEXT
);

CREATE TABLE IF NOT EXISTS Author (
    Author_ID INTEGER PRIMARY KEY,
    Name TEXT,
    Email TEXT,
    Phone TEXT
);

CREATE TABLE IF NOT EXISTS Item_Category (
    Category_ID INTEGER PRIMARY KEY,
    Type_type TEXT,
    Name TEXT
);

CREATE TABLE IF NOT EXISTS Item (
    Item_ID INTEGER PRIMARY KEY,
    Item_type TEXT,
    ISBN TEXT,
    Year INTEGER,
    Author_ID INTEGER,
    Category_ID INTEGER,
    Publisher_ID INTEGER,
    Pages INTEGER,
    Donor_ID INTEGER,
    FOREIGN KEY (Author_ID) REFERENCES Author(Author_ID),
    FOREIGN KEY (Category_ID) REFERENCES Item_Category(Category_ID)
);

CREATE TABLE IF NOT EXISTS Item_Copy (
    Copy_ID INTEGER PRIMARY KEY,
    Item_ID INTEGER,
    Condition_Status TEXT,
    Copy_Number TEXT,
    Library_ID INTEGER,
    FOREIGN KEY (Item_ID) REFERENCES Item(Item_ID),
    FOREIGN KEY (Library_ID) REFERENCES Library(Library_ID)
);

CREATE TABLE IF NOT EXISTS Loan (
    Loan_ID INTEGER PRIMARY KEY,
    Item_ID INTEGER,
    Issue_Date DATE,
    Due_Date DATE,
    Return_Date DATE,
    Member_ID INTEGER,
    Status TEXT,
    Copy_ID INTEGER,
    FOREIGN KEY (Item_ID) REFERENCES Item(Item_ID),
    FOREIGN KEY (Member_ID) REFERENCES Member(Member_ID),
    FOREIGN KEY (Copy_ID) REFERENCES Item_Copy(Copy_ID)
);

-- 📈 Analytics Enhancement Tables

-- Fact table for comprehensive loan analytics
CREATE TABLE IF NOT EXISTS Fact_Borrow_Events (
    Event_ID INTEGER PRIMARY KEY,
    Member_ID INTEGER,
    Item_ID INTEGER,
    Copy_ID INTEGER,
    Library_ID INTEGER,
    Borrow_Date DATE,
    Due_Date DATE,
    Return_Date DATE,
    Days_Borrowed INTEGER,
    Is_Overdue BOOLEAN,
    Days_Overdue INTEGER,
    Penalty_Amount REAL,
    Member_Type TEXT,
    Item_Category TEXT,
    Season TEXT,
    Day_of_Week TEXT,
    Is_Weekend BOOLEAN,
    FOREIGN KEY (Member_ID) REFERENCES Member(Member_ID),
    FOREIGN KEY (Item_ID) REFERENCES Item(Item_ID)
);

-- Member behavior analytics for predictive modeling
CREATE TABLE IF NOT EXISTS Member_Behavior_Analytics (
    Analytics_ID INTEGER PRIMARY KEY,
    Member_ID INTEGER,
    Analysis_Date DATE,
    Total_Books_Borrowed INTEGER,
    Books_Returned_On_Time INTEGER,
    Books_Returned_Late INTEGER,
    Average_Days_To_Return REAL,
    Favorite_Genre TEXT,
    Reading_Frequency_Score REAL,
    Member_Lifecycle_Stage TEXT,
    Last_Borrow_Date DATE,
    Days_Since_Last_Borrow INTEGER,
    Total_Penalties REAL,
    Penalty_Payment_Rate REAL,
    Preferred_Library_ID INTEGER,
    Risk_Score REAL,
    FOREIGN KEY (Member_ID) REFERENCES Member(Member_ID)
);

-- Model predictions storage
CREATE TABLE IF NOT EXISTS Prediction_Results (
    Prediction_ID INTEGER PRIMARY KEY,
    Model_Name TEXT,
    Model_Version TEXT,
    Prediction_Date DATETIME,
    Target_ID INTEGER,
    Target_Type TEXT,
    Prediction_Type TEXT,
    Predicted_Value REAL,
    Confidence_Score REAL,
    Actual_Value REAL,
    Is_Validated BOOLEAN
);
