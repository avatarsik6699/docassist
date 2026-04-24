import { renderToStaticMarkup } from "react-dom/server";

import HomeRoute, { meta } from "../app/routes/home";

describe("home route", () => {
  it("renders the Docassist headline", () => {
    const markup = renderToStaticMarkup(<HomeRoute />);

    expect(markup).toContain("Docassist");
    expect(meta()[0]).toEqual({ title: "Docassist" });
  });
});
