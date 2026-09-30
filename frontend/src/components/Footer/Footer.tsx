export function Footer() {
  const CURRENT_YEAR = new Date().getFullYear();

  return (
    <footer className="bg-blue-950 text-white">
      <div className="mx-auto max-w-7xl px-4 py-12">
        {/* Top Section */}
        <div className="mb-8 grid gap-8">
          {/* Brand */}
          <div>
            <div className="mb-4 flex items-center gap-2">
              {/* Logo/Icon */}
              <div className="flex h-8 w-8 items-center justify-center overflow-hidden rounded-lg">
                <img
                  src="/favicon.svg"
                  alt="community resources finder"
                  width={32}
                  height={32}
                  className="h-full w-full object-contain"
                />
              </div>
              <span className="font-bold text-white">Community Resources Finder</span>
            </div>
            <p className="text-sm text-gray-400">
              Website for a MVP (with the posibility to expand it) of an application to can
              translate a voice message into text and can set an implementation plan using
              comunitary resources of an specific zone to help unhoused people with AI models
              background.
            </p>
          </div>

          {/* Contact */}
          <div className="text-left">
            <h4 className="mb-4 font-semibold text-white">Contacto</h4>
            <ul className="space-y-2 text-sm">
              <li>
                <a href={`mailto:brunocesano20@gmail.com`} className="hover:text-blue-400">
                  Email: brunocesano20@gmail.com
                </a>
              </li>
              <li>
                <a href="https://github.com/bcesano20" className="hover:text-blue-400">
                  Github: github.com/bcesano20
                </a>
              </li>
            </ul>
          </div>
        </div>

        {/* Divider */}
        <hr className="border-gray-800" />

        {/* Bottom */}
        <div className="flex items-center justify-between pt-2 mx-auto text-[10px] text-gray-400">
          <p>
            &copy; {CURRENT_YEAR} Community Resources Finder. Todos los derechos reservados.
            <br />
            Version 1.0.0
          </p>
          <p> Desarrollado por Bruno Cesano</p>
        </div>
      </div>
    </footer>
  );
}
