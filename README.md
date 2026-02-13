# spring-2026-airline-reliability

The goal of this project is to train a model that would allow the user to input details about a potential flight (pre-existing or not) and return the odds that their flight is delayed and by how much. We then conduct a multivariate analysis of which factors affect reliability and timeliness in air travel in the US as measured through airline delays and cancelations.

There are a wide variety of factors to consider, such as the carrier strategy (hub and spoke model vs point to point), legacy vs budget airlines, origin and destination airports, cause of delay, etc. We would like to investigate how to these affect the on-time arrival and cancelation rates of the airlines and how do the different airlines fare when controlling for some of these factors.

Do different carriers strategies affect reliability given localized vs widespread weather events?
Certain airports/city markets are notoriously congested. When controlling for this does the disparities between different airlines vanish?
Do regional airlines fare better than national ones? Does this change when controlling for the number of weather-related disruptions in different regions?
Does any of this changes when considering pre- vs post- covid data? Do certain airline groups transition better than others?

We study this by using US flight data from the Bureau of Transportation Statistics from 2010 to 2024. We expect this to provide us enough data to do broad analysis but also be able to study potential differences in metrics pre- and post- pandemic. The dataset is rich in details of features we want to analyse such as geographic regions of origin and destination, carrier strategy (hub and spoke versus point to point), legacy versus budget airlines, localized or widespread weather events, special dates such as Christmas or Thanksgiving, flight duration (a longer flight might give the pilot more room to fly faster to arrive on time despite delayed departure). Some of these are not explictly in the data (e.g. carrier strategy), so it will also involve some domain knowledge to classify different airlines and/or airports.

Flight delays cost the US economy around $30 billion annually, and up to 37% of this ammount is composed of costs to individual passengers [1]. While most flight delays are inevitable, given the scale of this industry even small improvements can have significant impacts. We envision this tool to be useful to delay-sensitive customers, both in terms of airline/airport selection, but also for small-change differentiation - perhaps the 10am flight option is a lot better than the 12pm one. On the airline-level, while most delays are weather-related, this would provide a way to filter for the one which are not and may be able to be improved, or also when studying new potential routes and schedules which ones would likely have high delay rates - relating to weather or not.




[1] https://www.itij.com/latest/news/flight-disruption-impact-economy-and-environment#:~:text=The%20economic%20impact%20was%20investigated,also%20play%20a%20significant%20role
