import { render, screen } from "@testing-library/react"
import { BrowserRouter } from "react-router-dom"

import RestaurantCard from "../components/RestaurantCard/RestaurantCard"

describe("RestaurantCard", () => {
    test(
        "renders restaurant summary information",
        () => {
            render(
                <BrowserRouter>
                    <RestaurantCard
                        restaurant={{
                            id: 1,
                            name: "Wasabi Ramen",
                            cuisine: "Japanese",
                            rating: 4.5,
                            address: "123 Main St"
                        }}
                    />
                </BrowserRouter>
            );

            expect(
                screen.getAllByText(
                    "Wasabi Ramen"
                ).length
            ).toBeGreaterThan(0);

            expect(
                screen.getByText("Japanese")
            ).toBeInTheDocument();

            expect(
                screen.getByText(/4.5/)
            ).toBeInTheDocument();
        }
    )
})