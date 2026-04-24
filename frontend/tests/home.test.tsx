import { I18nextProvider } from "react-i18next";
import { renderToStaticMarkup } from "react-dom/server";

import { i18n } from "../app/shared/lib/i18n";
import HomeRoute, { meta } from "../app/routes/home";

describe("home route", () => {
  it("renders the Docassist headline", () => {
    const markup = renderToStaticMarkup(
      <I18nextProvider i18n={i18n}>
        <HomeRoute />
      </I18nextProvider>,
    );

    expect(markup).toContain("Docassist");
    expect(meta()[0]).toEqual({ title: "Docassist" });
  });
});
