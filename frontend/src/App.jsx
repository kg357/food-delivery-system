import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import RestaurantList from "./pages/RestaurantList/RestaurantList";
import RestaurantDetails from "./pages/RestaurantDetails/RestaurantDetails";
import MenuItemDetails from "./pages/MenuItemDetails/MenuItemDetails";
import EditMenuItem from "./pages/EditMenuItem/EditMenuItem";
import AddMenuItem from "./pages/AddMenuItem/AddMenuItem";

import "./App.css"

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route
          path="/"
          element={<Navigate to="/restaurants" />}
        />

        <Route
          path="/restaurants"
          element={<RestaurantList />}
        />

        <Route
          path="/restaurants/:id"
          element={<RestaurantDetails />}
        />

        <Route
          path="/restaurants/:id/menu/:itemId"
          element={<MenuItemDetails />}
        />

        <Route path="/menu/edit" element={<EditMenuItem />} />
        <Route path="/menu/add" element={<AddMenuItem />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App;