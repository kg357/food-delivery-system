import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import RestaurantList from "./pages/RestaurantList/RestaurantList";
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
        <Route path="/menu/edit" element={<EditMenuItem />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App;