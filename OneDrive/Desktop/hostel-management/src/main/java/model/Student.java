package com.hostel.model;

public class Student {
    private int id;
    private String regNo;
    private String name;
    private String department;
    private int year;
    private String phone;
    private String email;

    public Student() {
    }

    public Student(int id, String regNo, String name, String department,
                   int year, String phone, String email) {
        this.id = id;
        this.regNo = regNo;
        this.name = name;
        this.department = department;
        this.year = year;
        this.phone = phone;
        this.email = email;
    }

    public int getId() {
        return id;
    }

    public void setId(int id) {
        this.id = id;
    }

    public String getRegNo() {
        return regNo;
    }

    public void setRegNo(String regNo) {
        this.regNo = regNo;
    }

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public String getDepartment() {
        return department;
    }

    public void setDepartment(String department) {
        this.department = department;
    }

    public int getYear() {
        return year;
    }

    public void setYear(int year) {
        this.year = year;
    }

    public String getPhone() {
        return phone;
    }

    public void setPhone(String phone) {
        this.phone = phone;
    }

    public String getEmail() {
        return email;
    }

    public void setEmail(String email) {
        this.email = email;
    }
}
