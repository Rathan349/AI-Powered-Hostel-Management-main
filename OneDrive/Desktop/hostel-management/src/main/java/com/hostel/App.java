package com.hostel;

import com.hostel.config.DBUtil;

import java.sql.Connection;
import java.sql.DatabaseMetaData;
import java.sql.SQLException;

public class App {
    public static void main(String[] args) {
        System.out.println("Starting Hostel Management Launcher...");

        try (Connection conn = DBUtil.getConnection()) {
            if (conn != null && !conn.isClosed()) {
                DatabaseMetaData meta = conn.getMetaData();
                System.out.println("Database connection successful.");
                System.out.println("URL: " + meta.getURL());
                System.out.println("User: " + meta.getUserName());
            } else {
                System.err.println("Obtained null or closed connection.");
                System.exit(2);
            }
        } catch (SQLException e) {
            System.err.println("Database connection failed: " + e.getMessage());
            e.printStackTrace();
            System.exit(1);
        }

        System.out.println("Launcher finished.");
    }
}
