package com.hostel.servlet;

import com.hostel.dao.RoomDAO;
import com.hostel.model.Room;

import javax.servlet.ServletException;
import javax.servlet.annotation.WebServlet;
import javax.servlet.http.*;
import java.io.IOException;
import java.io.PrintWriter;
import java.util.List;

@WebServlet("/api/rooms")
public class RoomServlet extends HttpServlet {

    private RoomDAO roomDAO = new RoomDAO();

    @Override
    protected void doPost(HttpServletRequest request, HttpServletResponse response)
            throws ServletException, IOException {

        String blockName = request.getParameter("blockName");
        String roomNo = request.getParameter("roomNo");
        String capacityStr = request.getParameter("capacity");

        int capacity = 0;
        try {
            capacity = Integer.parseInt(capacityStr);
        } catch (NumberFormatException e) {
            capacity = 0;
        }

        Room r = new Room();
        r.setBlockName(blockName);
        r.setRoomNo(roomNo);
        r.setCapacity(capacity);
        r.setOccupied(0); // new room initially empty

        boolean added = roomDAO.addRoom(r);

        response.setContentType("application/json");
        PrintWriter out = response.getWriter();

        if (added) {
            out.print("{\"status\":\"success\"}");
        } else {
            out.print("{\"status\":\"error\",\"message\":\"Could not add room\"}");
        }
        out.flush();
    }

    @Override
    protected void doGet(HttpServletRequest request, HttpServletResponse response)
            throws ServletException, IOException {

        String type = request.getParameter("type");
        List<Room> rooms;

        if ("available".equalsIgnoreCase(type)) {
            rooms = roomDAO.getAvailableRooms();
        } else {
            rooms = roomDAO.getAllRooms();
        }

        response.setContentType("application/json");
        PrintWriter out = response.getWriter();

        out.print("[");
        for (int i = 0; i < rooms.size(); i++) {
            Room r = rooms.get(i);
            out.print("{");
            out.print("\"id\":" + r.getId() + ",");
            out.print("\"blockName\":\"" + r.getBlockName() + "\",");
            out.print("\"roomNo\":\"" + r.getRoomNo() + "\",");
            out.print("\"capacity\":" + r.getCapacity() + ",");
            out.print("\"occupied\":" + r.getOccupied());
            out.print("}");
            if (i != rooms.size() - 1) {
                out.print(",");
            }
        }
        out.print("]");
        out.flush();
    }
}
