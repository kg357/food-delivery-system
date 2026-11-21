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
import Register from "./pages/Register/Register";
import ProtectedRoute from "./components/ProtectedRoute/ProtectedRoute";
import LogoutButton from "./components/LogoutButton/LogoutButton";
import CustomerProfile from "./pages/CustomerProfile/CustomerProfile";
import Cart from "./pages/Cart/Cart";
import OrderConfirmation from "./pages/OrderConfirmation/OrderConfirmation";
import OrderHistory from "./pages/OrderHistory/OrderHistory";

import "./App.css"

function App() {
  return (
    <BrowserRouter>
      <Routes>


        <Route
            path="/register"
            element={<Register />}
        />

        <Route 
          path="/" 
          element={<Login />} 
        />


        {/* Administrator routes */}
        <Route
            element={
                <ProtectedRoute allowedRoles={["admin"]} />
            }
        >
            <Route
                path="/admin"
                element={
                    <main style={{ padding: "40px", textAlign: "left" }}>
                        <LogoutButton />

                        <h1>Administrator Dashboard</h1>

                        <p>
                            Administrator functionality coming soon.
                        </p>
                    </main>
                }
            />
        </Route>


        <Route
          path="/owner/restaurants/new"
          element={<CreateRestaurant />}
        />



        {/* Customer-only routes */}
        <Route
            element={
                <ProtectedRoute allowedRoles={["customer"]} />
            }
        >

            <Route
                path="/cart"
                element={<Cart />}
            />

            <Route
                path="/orders"
                element={<OrderHistory />}
            />

            <Route
                path="/orders/:orderId"
                element={<OrderConfirmation />}
            />

            <Route
                path="/account"
                element={<CustomerProfile />}
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
        </Route>



        {/* Restaurant owner routes */}
        <Route
            element={
                <ProtectedRoute
                    allowedRoles={["restaurant_owner"]}
                />
            }
        >
            <Route
                path="/owner/restaurants"
                element={<OwnerDashboard />}
            />

            <Route
                path="/owner/restaurants/new"
                element={<CreateRestaurant />}
            />

            <Route
                path="/owner/restaurants/:id"
                element={<OwnerRestaurantDetails />}
            />

            <Route
                path="/owner/restaurants/:id/menu/edit"
                element={<EditMenuItem />}
            />

            <Route
                path="/owner/restaurants/:id/menu/add"
                element={<AddMenuItem />}
            />

            {/* Existing legacy menu routes */}
            <Route path="/menu/edit" element={<EditMenuItem />} />
            <Route path="/menu/add" element={<AddMenuItem />} />
        </Route>

      </Routes>
    </BrowserRouter>
  )
}

export default App;