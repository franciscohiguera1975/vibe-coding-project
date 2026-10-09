import { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Link } from 'react-router-dom';

export interface HeroSlide {
  image: string;
  eyebrow: string;
  title: string;
  description: string;
  primaryCta: { label: string; to: string };
  secondaryCta: { label: string; to: string };
}

interface HeroCarouselProps {
  slides: HeroSlide[];
  /** Milisegundos entre avances automáticos; 0 desactiva el autoplay. */
  intervalMs?: number;
}

/** Carousel del hero: sin dependencias externas (una franja de slides trasladada
 * por índice), con autoplay que se pausa al interactuar con las flechas o los
 * indicadores para no pelear con la elección del usuario. */
export function HeroCarousel({ slides, intervalMs = 7000 }: HeroCarouselProps) {
  const { t } = useTranslation();
  const [index, setIndex] = useState(0);

  useEffect(() => {
    if (intervalMs <= 0 || slides.length <= 1) return;
    const id = setInterval(() => setIndex((i) => (i + 1) % slides.length), intervalMs);
    return () => clearInterval(id);
  }, [intervalMs, slides.length]);

  function goTo(i: number) {
    setIndex((i + slides.length) % slides.length);
  }

  return (
    <div className="relative overflow-hidden">
      <div
        className="flex transition-transform duration-700 ease-out"
        style={{ transform: `translateX(-${index * 100}%)` }}
      >
        {slides.map((slide) => (
          <div key={slide.title} className="relative w-full shrink-0">
            <div
              className="h-[32rem] bg-cover bg-center sm:h-[36rem]"
              style={{ backgroundImage: `url(${slide.image})` }}
            >
              <div className="h-full w-full bg-navy-950/70">
                <div className="mx-auto flex h-full max-w-7xl items-center px-4 sm:px-6 lg:px-8">
                  <div className="max-w-2xl">
                    <span className="badge bg-brand-400/20 text-brand-200">{slide.eyebrow}</span>
                    <h1 className="mt-4 text-4xl font-bold tracking-tight text-white sm:text-5xl">
                      {slide.title}
                    </h1>
                    <p className="mt-4 text-lg text-ink-100">{slide.description}</p>
                    <div className="mt-8 flex flex-wrap gap-3">
                      <Link
                        to={slide.primaryCta.to}
                        className="btn-primary bg-brand-500 text-white hover:bg-brand-400"
                      >
                        {slide.primaryCta.label}
                      </Link>
                      <Link
                        to={slide.secondaryCta.to}
                        className="btn-secondary bg-transparent text-white ring-white/40 hover:bg-white/10"
                      >
                        {slide.secondaryCta.label}
                      </Link>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      {slides.length > 1 && (
        <>
          <div className="absolute right-6 top-1/2 hidden -translate-y-1/2 flex-col gap-3 sm:flex">
            <button
              type="button"
              aria-label={t('heroCarousel.previous')}
              onClick={() => goTo(index - 1)}
              className="flex h-10 w-10 items-center justify-center rounded border border-white/40 text-white transition-colors hover:bg-white/10"
            >
              ‹
            </button>
            <button
              type="button"
              aria-label={t('heroCarousel.next')}
              onClick={() => goTo(index + 1)}
              className="flex h-10 w-10 items-center justify-center rounded border border-white/40 text-white transition-colors hover:bg-white/10"
            >
              ›
            </button>
          </div>

          <div className="absolute bottom-5 left-1/2 flex -translate-x-1/2 gap-2">
            {slides.map((slide, i) => (
              <button
                key={slide.title}
                type="button"
                aria-label={t('heroCarousel.goToSlide', { number: i + 1 })}
                onClick={() => goTo(i)}
                className={`h-2 w-2 rounded-full transition-colors ${
                  i === index ? 'bg-brand-400' : 'bg-white/40 hover:bg-white/60'
                }`}
              />
            ))}
          </div>
        </>
      )}
    </div>
  );
}
