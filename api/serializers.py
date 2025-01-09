from rest_framework import serializers
from support_scheduler.request import ScheduleParameters, GAParameters

from api.dto import ScheduleRequest


def default_genetic_algorithm_parameters():
    return GAParameters(
        seed=10,
        generations=200,
        population_size=500,
        crossover_rate=0.7,
        mutation_rate=0.3,
    )


class ScheduleRequestSerializer(serializers.Serializer):
    schedule_parameters = serializers.SerializerMethodField()
    genetic_algorithm_parameters = serializers.SerializerMethodField()

    def get_schedule_parameters(self, instance):
        return ScheduleParametersSerializer(instance.schedule_parameters).data

    def get_genetic_algorithm_parameters(self, instance):
        if instance.genetic_algorithm_parameters is None:
            return default_genetic_algorithm_parameters()
        else:
            return GeneticAlgorithmParametersSerializer(instance.genetic_algorithm_parameters).data

    def to_internal_value(self, data):
        schedule_parameters = ScheduleParametersSerializer(data=data.get('schedule_parameters'))
        if not schedule_parameters.is_valid():
            raise serializers.ValidationError({"schedule_parameters": schedule_parameters.errors})
        schedule_parameters.save()

        genetic_algorithm_parameters = None
        genetic_algorithm_raw_data = data.get('genetic_algorithm_parameters')
        if genetic_algorithm_raw_data is not None:
            genetic_algorithm_parameters = GeneticAlgorithmParametersSerializer(data=genetic_algorithm_raw_data)
            if not genetic_algorithm_parameters.is_valid():
                raise serializers.ValidationError({"genetic_algorithm_parameters": genetic_algorithm_parameters.errors})
            genetic_algorithm_parameters.save()

        return {
            'schedule_parameters': schedule_parameters.instance,
            'genetic_algorithm_parameters': None if genetic_algorithm_parameters is None else genetic_algorithm_parameters.instance
        }

    def create(self, validated_data):
        schedule_parameters = validated_data.pop('schedule_parameters')
        genetic_algorithm_parameters = validated_data.pop('genetic_algorithm_parameters')
        if genetic_algorithm_parameters is None:
            genetic_algorithm_parameters = default_genetic_algorithm_parameters()
        return ScheduleRequest(schedule_parameters, genetic_algorithm_parameters)

    def update(self, instance, validated_data):
        instance.schedule_parameters = validated_data.get('schedule_parameters', instance.schedule_parameters)
        instance.genetic_algorithm_parameters = validated_data.get('genetic_algorithm_parameters',
                                                                   instance.genetic_algorithm_parameters)
        return instance


class ScheduleParametersSerializer(serializers.Serializer):
    schedule_start_date = serializers.DateTimeField()
    schedule_end_date = serializers.DateTimeField()
    devs = serializers.ListField(child=serializers.CharField())
    dev_leave_days = serializers.DictField(child=serializers.ListField(child=serializers.DateTimeField()), default={})
    dev_preferred_days = serializers.DictField(child=serializers.ListField(child=serializers.DateTimeField()),
                                               default={}, allow_null=True)
    dimensions = serializers.IntegerField(default=1)

    def create(self, validated_data):
        return ScheduleParameters(**validated_data)

    def update(self, instance, validated_data):
        instance.schedule_start_date = validated_data.get('schedule_start_date', instance.schedule_start_date)
        instance.schedule_end_date = validated_data.get('schedule_end_date', instance.schedule_end_date)
        instance.devs = validated_data.get('devs', instance.devs)
        instance.dev_leave_days = validated_data.get('dev_leave_days', instance.dev_leave_days)
        instance.dev_preferred_days = validated_data.get('dev_preferred_days', instance.dev_preferred_days)
        instance.dimensions = validated_data.get('dimensions', instance.dimensions)
        return ScheduleParameters(**validated_data)


class GeneticAlgorithmParametersSerializer(serializers.Serializer):
    seed = serializers.IntegerField()
    generations = serializers.IntegerField()
    population_size = serializers.IntegerField()
    crossover_rate = serializers.FloatField()
    mutation_rate = serializers.FloatField()

    def create(self, validated_data):
        return GAParameters(**validated_data)

    def update(self, instance, validated_data):
        instance.seed = validated_data.get('seed', instance.seed)
        instance.generations = validated_data.get('generations', instance.generations)
        instance.population_size = validated_data.get('population_size', instance.population_size)
        instance.crossover_rate = validated_data.get('crossover_rate', instance.crossover_rate)
        instance.mutation_rate = validated_data.get('mutation_rate', instance.mutation_rate)
        return GAParameters(**validated_data)
