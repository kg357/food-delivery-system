import { BrowserRouter, Routes, Route, Link } from "react-router-dom";
import RestaurantList from "./pages/RestaurantList/RestaurantList";
import RestaurantDetails from "./pages/RestaurantDetails/RestaurantDetails";
import MenuItemDetails from "./pages/MenuItemDetails/MenuItemDetails";
import EditMenuItem from "./pages/EditMenuItem/EditMenuItem";
import AddMenuItem from "./pages/AddMenuItem/AddMenuItem";
import Login from "./pages/Login/Login";
import CreateRestaurant from "./pages/CreateRestaurant/CreateRestaurant";
import OwnerDashboard from "./pages/OwnerDashboard/OwnerDashboard";
import OwnerRestaurantDetails from "./pages/OwnerRestaurantDetails/OwnerRestaurantDetails";

import "./App.css"

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route 
          path="/" 
          element={<Login />} 
        />

        <Route
          path="/owner/restaurants"
          element={<OwnerDashboard />}
        />

        <Route
          path="/admin"
          element={
            <main style={{ padding: "40px", textAlign: "left" }}>
              <Link
                to="/"
                className="back-to-login"
                onClick={() => sessionStorage.removeItem("demoRole")}
              >
                ← Back to Login
              </Link>

              <h1>Administrator Dashboard</h1>
              <p>Administrator functionality coming soon.</p>
            </main>
          }
        />

        <Route
          path="/owner/restaurants/new"
          element={<CreateRestaurant />}
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
          path="/owner/restaurants/:id"
          element={<OwnerRestaurantDetails />}
        />

        <Route
          path="/restaurants/:id/menu/:itemId"
          element={<MenuItemDetails />}
        />

        <Route
          path="/owner/restaurants/:id/menu/edit"
          element={<EditMenuItem />}
        />

        <Route
          path="/owner/restaurants/:id/menu/add"
          element={<AddMenuItem />}
        />

        <Route path="/menu/edit" element={<EditMenuItem />} />
        <Route path="/menu/add" element={<AddMenuItem />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App;