import { render, screen }
    from "@testing-library/react";

import Loading
    from "../components/Loading/Loading";

describe("Loading", () => {
    test(
        "shows loading message",
        () => {
            render(<Loading />);
            expect(
                screen.getByText(/loading/i)
            ).toBeInTheDocument();

        }
    );

});