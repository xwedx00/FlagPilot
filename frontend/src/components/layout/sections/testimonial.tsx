"use client"
import { Star } from "lucide-react"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import {
    Card,
    CardContent,
    CardDescription,
    CardHeader,
    CardTitle
} from "@/components/ui/card"
import {
    Carousel,
    CarouselContent,
    CarouselItem,
    CarouselNext,
    CarouselPrevious
} from "@/components/ui/carousel"

interface ReviewProps {
    image: string
    name: string
    userName: string
    comment: string
    rating: number
}

const reviewList: ReviewProps[] = [
    {
        image: "https://ui-avatars.com/api/?name=John+Doe&background=6366f1&color=fff&size=128",
        name: "John Doe",
        userName: "Product Manager",
        comment:
            "Wow this is awesome!. This Starter Kit lets me change colors, fonts and images to match my brand identity. ",
        rating: 5.0
    },
    {
        image: "https://ui-avatars.com/api/?name=Sophia+Collins&background=8b5cf6&color=fff&size=128",
        name: "Sophia Collins",
        userName: "Cybersecurity Analyst",
        comment:
            "The security implementation is top-notch. Built-in authentication and proper data validation give me confidence in the platform. ",
        rating: 4.8
    },

    {
        image: "https://ui-avatars.com/api/?name=Adam+Johnson&background=ec4899&color=fff&size=128",
        name: "Adam Johnson",
        userName: "Chief Technology Officer",
        comment:
            "Perfect architecture and clean code structure. Our development team was able to scale quickly without technical debt issues.",
        rating: 4.9
    },
    {
        image: "https://ui-avatars.com/api/?name=Ethan+Parker&background=14b8a6&color=fff&size=128",
        name: "Ethan Parker",
        userName: "Data Scientist",
        comment:
            "The analytics integration capabilities are excellent. Easy to implement tracking and gather meaningful insights from user behavior.",
        rating: 5.0
    },
    {
        image: "https://ui-avatars.com/api/?name=Ava+Mitchell&background=f59e0b&color=fff&size=128",
        name: "Ava Mitchell",
        userName: "IT Project Manager",
        comment:
            "Streamlined our deployment process significantly. The documentation and setup guide helped our team deliver projects faster.",
        rating: 5.0
    },
    {
        image: "https://ui-avatars.com/api/?name=Isabella+Reed&background=3b82f6&color=fff&size=128",
        name: "Isabella Reed",
        userName: "DevOps Engineer",
        comment:
            "Amazing CI/CD integration and containerization support. The deployment pipeline configurations saved us weeks of setup time.",
        rating: 4.9
    }
]

export const TestimonialSection = () => {
    return (
        <section id="testimonials" className="container mx-auto px-4 py-16 sm:py-20">
            <div className="mb-8 text-center">
                <h2 className="mb-2 text-center text-lg text-primary tracking-wider">
                    Testimonials
                </h2>

                <h2 className="mb-4 text-center font-bold text-3xl md:text-4xl">
                    Hear What Our 1000+ Clients Say
                </h2>
            </div>

            <Carousel
                opts={{
                    align: "start"
                }}
                className="relative mx-auto w-[80%] sm:w-[90%] lg:max-w-screen-xl"
            >
                <CarouselContent>
                    {reviewList.map((review) => (
                        <CarouselItem
                            key={review.name}
                            className="md:basis-1/2 lg:basis-1/3"
                        >
                            <Card className="flex h-full flex-col bg-muted/50">
                                <CardContent className="flex flex-grow flex-col">
                                    <div className="flex gap-1 pb-4">
                                        <Star className="size-4 fill-primary text-primary" />
                                        <Star className="size-4 fill-primary text-primary" />
                                        <Star className="size-4 fill-primary text-primary" />
                                        <Star className="size-4 fill-primary text-primary" />
                                        <Star className="size-4 fill-primary text-primary" />
                                    </div>
                                    <div className="flex flex-1 items-start pb-4">
                                        <p className="text-sm leading-relaxed">{`"${review.comment}"`}</p>
                                    </div>
                                </CardContent>

                                <CardHeader >
                                    <div className="flex flex-row items-center gap-4">
                                        <Avatar>
                                            <AvatarImage
                                                src={review.image}
                                                alt="radix"
                                            />
                                            <AvatarFallback>SV</AvatarFallback>
                                        </Avatar>

                                        <div className="flex flex-col">
                                            <CardTitle className="text-lg">
                                                {review.name}
                                            </CardTitle>
                                            <CardDescription>
                                                {review.userName}
                                            </CardDescription>
                                        </div>
                                    </div>
                                </CardHeader>
                            </Card>
                        </CarouselItem>
                    ))}
                </CarouselContent>
                <CarouselPrevious />
                <CarouselNext />
            </Carousel>
        </section>
    )
}
