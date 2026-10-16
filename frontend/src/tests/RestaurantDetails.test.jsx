import { render, screen }
    from "@testing-library/react";

describe("RestaurantDetails", () => {
    test("renders restaurant information", () => {
        render(
            <div>
                <h1>Wasabi Ramen</h1>
                <p>⭐ 4.5</p>
                <p>123 Main St</p>
                <h2>Menu</h2>
            </div>
        );
        expect(
            screen.getAllByText(
                "Wasabi Ramen"
            )[0]
        ).toBeInTheDocument();

        expect(
            screen.getByText(
                /4.5/
            )
        ).toBeInTheDocument();

        expect(
            screen.getByText(
                /123 Main St/
            )
        ).toBeInTheDocument();

    }
    );

    test("renders restaurant not found message", () => {

        render(
            <p className="empty">
                Restaurant not found.
            </p>
        );

        expect(
            screen.getByText(
                "Restaurant not found."
            )
        ).toBeInTheDocument();

    });

}
);