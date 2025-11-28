package com.hostel.servlet;

import com.hostel.dao.UserDAO;

import javax.servlet.ServletException;
import javax.servlet.annotation.WebServlet;
import javax.servlet.http.*;
import java.io.IOException;
import java.io.PrintWriter;

@WebServlet("/api/login")
public class LoginServlet extends HttpServlet {

    private UserDAO userDAO = new UserDAO();

    @Override
    protected void doPost(HttpServletRequest request, HttpServletResponse response)
            throws ServletException, IOException {

        String username = request.getParameter("username");
        String password = request.getParameter("password");

        boolean valid = userDAO.validateLogin(username, password);

        response.setContentType("application/json");
        PrintWriter out = response.getWriter();

        if (valid) {
            HttpSession session = request.getSession();
            session.setAttribute("username", username);
            out.print("{\"status\":\"success\"}");
        } else {
            out.print("{\"status\":\"error\",\"message\":\"Invalid credentials\"}");
        }
        out.flush();
    }
}
