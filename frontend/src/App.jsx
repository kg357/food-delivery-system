import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import RestaurantList from "./pages/RestaurantList/RestaurantList";
import RestaurantDetails from "./pages/RestaurantDetails/RestaurantDetails";
import EditMenuItem from "./pages/EditMenuItem/EditMenuItem";

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

        <Route path="/menu/edit" element={<EditMenuItem />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App;